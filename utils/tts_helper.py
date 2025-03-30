import os
import asyncio
import logging
import edge_tts

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
                'display_name': f"{voice['Locale']} - {voice['DisplayName']} ({voice['Gender']})"
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
