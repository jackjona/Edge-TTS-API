import os
import asyncio
import logging
import edge_tts
from flask import Response

# Configure logging
logger = logging.getLogger(__name__)

async def get_available_voices():
    """
    Get all available voices from edge-tts.
    
    Returns:
        list: List of voice objects with name, gender, and locale
    """
    try:
        voices = await edge_tts.list_voices()
        # Format voices for better usability
        formatted_voices = []
        for voice in voices:
            voice_obj = {
                'name': voice["ShortName"],
                'gender': voice["Gender"],
                'locale': voice["Locale"],
                'display_name': f"{voice['Locale']} - {voice['FriendlyName']} ({voice['Gender']})"
            }
            formatted_voices.append(voice_obj)
            
        # Sort voices by locale
        formatted_voices.sort(key=lambda x: x['locale'])
        return formatted_voices
    except Exception as e:
        logger.exception("Error getting available voices: %s", str(e))
        raise

async def generate_speech(text, voice, output_path, format='mp3'):
    """
    Generate speech from text using edge-tts.
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice to use (e.g., 'en-US-ChristopherNeural')
        output_path (str): Path to save the audio file
        format (str): Audio format (mp3 or wav)
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Create communicate object
        communicate = edge_tts.Communicate(text, voice)
        
        # Generate speech
        await communicate.save(output_path)
        
        # Return the path to the generated file
        return output_path
    except Exception as e:
        logger.exception("Error generating speech: %s", str(e))
        raise

async def stream_speech_generator(text, voice):
    """
    Generate speech from text using edge-tts and stream it directly.
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice to use (e.g., 'en-US-ChristopherNeural')
        
    Yields:
        bytes: Audio data chunks
    """
    try:
        # Create communicate object
        communicate = edge_tts.Communicate(text, voice)
        
        # Stream the audio data
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    except Exception as e:
        logger.exception("Error streaming speech: %s", str(e))
        raise

def create_stream_response(text, voice, format='mp3'):
    """
    Create a Flask response for streaming audio.
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice to use (e.g., 'en-US-ChristopherNeural')
        format (str): Audio format (mp3 or wav)
        
    Returns:
        Response: A Flask response object that streams the audio
    """
    # Set appropriate content type based on format
    content_type = 'audio/mpeg' if format == 'mp3' else 'audio/wav'
    
    # Create a generator function that will run the async code in a synchronous context
    def generate():
        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get the async generator
            stream_gen = stream_speech_generator(text, voice)
            
            # Run the generator and yield chunks
            while True:
                try:
                    # Get the next chunk
                    chunk = loop.run_until_complete(stream_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    # End of stream
                    break
        finally:
            # Clean up
            loop.close()
    
    # Return the Flask response object
    return Response(generate(), mimetype=content_type)
