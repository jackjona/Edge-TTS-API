import os
import logging
import uuid
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import tempfile
import asyncio
from utils.tts_helper import get_available_voices, generate_speech

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "edge-tts-secret-key")

# Configure logging
logger = logging.getLogger(__name__)

# Configure temp directory for audio files
TEMP_DIR = tempfile.gettempdir()
os.makedirs(os.path.join(TEMP_DIR, "edge_tts_audio"), exist_ok=True)
AUDIO_FOLDER = os.path.join(TEMP_DIR, "edge_tts_audio")

# Main route - renders the web interface
@app.route('/')
def index():
    try:
        # Get available voices using the helper function
        voices = asyncio.run(get_available_voices())
        return render_template('index.html', voices=voices)
    except Exception as e:
        logger.exception("Error loading voices: %s", str(e))
        return render_template('index.html', voices=[], error="Failed to load voices. Please try again later.")

# API endpoint for text-to-speech conversion
@app.route('/api/tts', methods=['POST'])
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
        file_url = url_for('get_audio', filename=filename)
        return jsonify({"success": True, "file_url": file_url})
    except Exception as e:
        logger.exception("Error in TTS API: %s", str(e))
        return jsonify({"error": str(e)}), 500

# Web interface for text-to-speech conversion
@app.route('/convert', methods=['POST'])
def convert_text():
    try:
        # Get form data
        text = request.form.get('text', '')
        voice = request.form.get('voice', 'en-US-ChristopherNeural')
        audio_format = request.form.get('format', 'mp3').lower()
        
        # Validate inputs
        if not text:
            flash("Please enter some text to convert.", "error")
            return redirect(url_for('index'))
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{audio_format}"
        output_path = os.path.join(AUDIO_FOLDER, filename)
        
        # Generate speech
        asyncio.run(generate_speech(text, voice, output_path, audio_format))
        
        # Return the audio file URL
        file_url = url_for('get_audio', filename=filename)
        return render_template('index.html', 
                             audio_url=file_url, 
                             text=text, 
                             selected_voice=voice, 
                             voices=asyncio.run(get_available_voices()),
                             selected_format=audio_format)
    except Exception as e:
        logger.exception("Error in convert text: %s", str(e))
        flash(f"Error converting text: {str(e)}", "error")
        return redirect(url_for('index'))

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
def get_voices_api():
    try:
        voices = asyncio.run(get_available_voices())
        return jsonify({"voices": voices})
    except Exception as e:
        logger.exception("Error getting voices: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
