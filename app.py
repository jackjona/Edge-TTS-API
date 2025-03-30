import os
import logging
import uuid
import secrets
import time
import threading
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file, url_for, send_from_directory
import tempfile
import asyncio
from dotenv import load_dotenv
from utils.tts_helper import get_available_voices, generate_speech, create_stream_response

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# API Authentication
# Get API key from environment or use the hardcoded default
API_KEY = os.environ.get("API_KEY", "edge_tts_api_key_12345")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if API key is provided in the request
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        # If no API key is provided or the API key is invalid
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Unauthorized. Invalid or missing API key."}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure temp directory for audio files
TEMP_DIR = tempfile.gettempdir()
AUDIO_FOLDER_NAME = os.environ.get("AUDIO_FOLDER_NAME", "edge_tts_audio")
os.makedirs(os.path.join(TEMP_DIR, AUDIO_FOLDER_NAME), exist_ok=True)
AUDIO_FOLDER = os.path.join(TEMP_DIR, AUDIO_FOLDER_NAME)

# Get maximum age for audio files in seconds (default: 1 hour)
AUDIO_MAX_AGE = int(os.environ.get("AUDIO_MAX_AGE", 3600))

# Function to clean up old audio files
def cleanup_old_audio_files():
    """Remove audio files older than AUDIO_MAX_AGE seconds"""
    try:
        current_time = time.time()
        file_count = 0
        for filename in os.listdir(AUDIO_FOLDER):
            file_path = os.path.join(AUDIO_FOLDER, filename)
            # Check if file is older than AUDIO_MAX_AGE
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > AUDIO_MAX_AGE:
                os.remove(file_path)
                file_count += 1
        if file_count > 0:
            logger.info(f"Cleaned up {file_count} audio files older than {AUDIO_MAX_AGE} seconds")
    except Exception as e:
        logger.error(f"Error cleaning up audio files: {str(e)}")

# Clean up old files at startup
cleanup_old_audio_files()

# Set up a background thread to clean up old files periodically

def periodic_cleanup():
    """Run cleanup at regular intervals"""
    while True:
        # Sleep for 15 minutes
        time.sleep(900)
        cleanup_old_audio_files()

# Start the cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()
logger.info("Started periodic cleanup thread (every 15 minutes)")

# Get configuration from environment variables
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))

# API root - display API information
@app.route('/')
def index():
    return jsonify({
        "name": "Edge TTS API",
        "version": "1.0.0",
        "description": "A REST API for Microsoft Edge TTS",
        "endpoints": {
            "voices": "/api/voices",
            "tts": "/api/tts",
            "stream": "/api/stream"
        },
        "demo": "/demo/stream",
        "documentation": "Include X-API-Key header or api_key query parameter with all requests. See the .env file for API key configuration."
    })

# API endpoint for text-to-speech conversion
@app.route('/api/tts', methods=['POST'])
@require_api_key
def tts_api():
    try:
        # Get data from request
        data = request.json or {}
        text = data.get('text', '')
        voice = data.get('voice', 'en-US-ChristopherNeural')
        audio_format = data.get('format', 'mp3').lower()
        direct_download = request.args.get('direct', 'false').lower() == 'true'
        
        # Validate inputs
        if not text:
            return jsonify({"error": "Text is required"}), 400
            
        # Check text length (limit to 5000 characters)
        MAX_TEXT_LENGTH = 5000
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                "error": f"Text length exceeds maximum limit of {MAX_TEXT_LENGTH} characters. Your text is {len(text)} characters long."
            }), 400
            
        # Validate audio format
        ALLOWED_FORMATS = ['mp3', 'wav']
        if audio_format not in ALLOWED_FORMATS:
            return jsonify({
                "error": f"Invalid audio format: {audio_format}. Allowed formats are: {', '.join(ALLOWED_FORMATS)}"
            }), 400
            
        # Validate voice (check if the voice exists)
        try:
            available_voices = asyncio.run(get_available_voices())
            voice_ids = [v['name'] for v in available_voices]
            if voice not in voice_ids:
                return jsonify({
                    "error": f"Invalid voice: {voice}. Use /api/voices endpoint to get a list of available voices."
                }), 400
        except Exception as e:
            logger.warning(f"Failed to validate voice: {str(e)}")
            # If voice validation fails, we'll proceed with the provided voice and let Edge TTS handle any errors
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{audio_format}"
        output_path = os.path.join(AUDIO_FOLDER, filename)
        
        # Generate speech
        asyncio.run(generate_speech(text, voice, output_path, audio_format))
        
        # Return the audio file directly if direct_download is True
        if direct_download:
            # Determine content type based on file extension
            content_type = 'audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
            return send_file(output_path, mimetype=content_type, as_attachment=True, 
                            download_name=f"tts-{voice}-{uuid.uuid4().hex[:8]}.{audio_format}")
        
        # Otherwise return a URL to access the audio file
        file_url = url_for('get_audio', filename=filename, _external=True)
        return jsonify({
            "success": True, 
            "file_url": file_url,
            "text": text,
            "voice": voice,
            "format": audio_format
        })
    except Exception as e:
        logger.exception("Error in TTS API: %s", str(e))
        return jsonify({"error": str(e)}), 500

# Route to serve generated audio files
@app.route('/audio/<filename>')
def get_audio(filename):
    try:
        file_path = os.path.join(AUDIO_FOLDER, filename)
        # Determine content type based on file extension
        content_type = 'audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "Audio file not found"}), 404
            
        # Serve the file
        return send_file(file_path, mimetype=content_type, as_attachment=True)
    except Exception as e:
        logger.exception("Error serving audio file: %s", str(e))
        return jsonify({"error": str(e)}), 500

# Route to get available voices (JSON API)
@app.route('/api/voices', methods=['GET'])
@require_api_key
def get_voices_api():
    try:
        voices = asyncio.run(get_available_voices())
        return jsonify({"voices": voices})
    except Exception as e:
        logger.exception("Error getting voices: %s", str(e))
        return jsonify({"error": str(e)}), 500

# API endpoint for streaming text-to-speech
@app.route('/api/stream', methods=['POST'])
@require_api_key
def stream_tts_api():
    try:
        # Get data from request
        data = request.json or {}
        text = data.get('text', '')
        voice = data.get('voice', 'en-US-ChristopherNeural')
        audio_format = data.get('format', 'mp3').lower()
        
        # Validate inputs
        if not text:
            return jsonify({"error": "Text is required"}), 400
            
        # Check text length (limit to 5000 characters)
        MAX_TEXT_LENGTH = 5000
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                "error": f"Text length exceeds maximum limit of {MAX_TEXT_LENGTH} characters. Your text is {len(text)} characters long."
            }), 400
            
        # Validate audio format
        ALLOWED_FORMATS = ['mp3', 'wav']
        if audio_format not in ALLOWED_FORMATS:
            return jsonify({
                "error": f"Invalid audio format: {audio_format}. Allowed formats are: {', '.join(ALLOWED_FORMATS)}"
            }), 400
            
        # Validate voice (check if the voice exists)
        try:
            available_voices = asyncio.run(get_available_voices())
            # Use the same key structure as in the get_available_voices() function
            voice_ids = [v['name'] for v in available_voices]
            if voice not in voice_ids:
                return jsonify({
                    "error": f"Invalid voice: {voice}. Use /api/voices endpoint to get a list of available voices."
                }), 400
        except Exception as e:
            logger.warning(f"Failed to validate voice: {str(e)}")
            # If voice validation fails, we'll proceed with the provided voice and let Edge TTS handle any errors
        
        # Stream the audio data
        logger.info(f"Streaming TTS: text='{text[:50]}...' voice={voice} format={audio_format}")
        
        # Add a generation timestamp to the response headers
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = create_stream_response(text, voice, audio_format)
        response.headers['X-Generation-Timestamp'] = timestamp
        return response
        
    except Exception as e:
        logger.exception("Error in streaming TTS API: %s", str(e))
        return jsonify({"error": str(e)}), 500

# Serve static files from the static folder
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Demo web page for streaming TTS
@app.route('/demo/stream')
def stream_demo():
    return send_from_directory('static', 'stream_demo.html')

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
