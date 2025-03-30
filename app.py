import os
import logging
import uuid
import secrets
from functools import wraps
from flask import Flask, request, jsonify, send_file, url_for
import tempfile
import asyncio
from utils.tts_helper import get_available_voices, generate_speech

# Create Flask app
app = Flask(__name__)

# API Authentication
# Get API key from environment or generate a secure one
API_KEY = os.environ.get("API_KEY", secrets.token_urlsafe(32))

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
os.makedirs(os.path.join(TEMP_DIR, "edge_tts_audio"), exist_ok=True)
AUDIO_FOLDER = os.path.join(TEMP_DIR, "edge_tts_audio")

# API root - display API information
@app.route('/')
def index():
    return jsonify({
        "name": "Edge TTS API",
        "version": "1.0.0",
        "description": "A REST API for Microsoft Edge TTS",
        "endpoints": {
            "voices": "/api/voices",
            "tts": "/api/tts"
        },
        "documentation": "Include X-API-Key header or api_key query parameter with all requests",
        "api_key": API_KEY
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
        
        # Validate inputs
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{audio_format}"
        output_path = os.path.join(AUDIO_FOLDER, filename)
        
        # Generate speech
        asyncio.run(generate_speech(text, voice, output_path, audio_format))
        
        # Return a URL to access the audio file
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
