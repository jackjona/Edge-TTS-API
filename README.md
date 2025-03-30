# Edge TTS API

A REST API for Microsoft Edge Text-to-Speech service, providing high-quality text-to-speech conversion with multiple voices and language options.

## API Endpoints

### Root Endpoint

```
GET /
```

Returns basic API information about the service.

**Example Response:**
```json
{
  "name": "Edge TTS API",
  "version": "1.0.0",
  "description": "A REST API for Microsoft Edge TTS",
  "endpoints": {
    "voices": "/api/voices",
    "tts": "/api/tts"
  },
  "authentication": "Include X-API-Key header or api_key query parameter with all requests",
  "documentation": "See README.md for detailed API documentation"
}
```

### Get Available Voices

```
GET /api/voices
```

Returns a list of all available voices with their details.

**Authentication Required:** Yes (API Key)

**Example Response:**
```json
{
  "voices": [
    {
      "name": "en-US-ChristopherNeural",
      "gender": "Male",
      "locale": "en-US",
      "display_name": "en-US - Microsoft Christopher Online (Natural) - English (United States) (Male)"
    },
    {
      "name": "ja-JP-NanamiNeural",
      "gender": "Female",
      "locale": "ja-JP",
      "display_name": "ja-JP - Microsoft Nanami Online (Natural) - Japanese (Japan) (Female)"
    },
    // More voices...
  ]
}
```

### Text-to-Speech Conversion

```
POST /api/tts
```

Converts text to speech and returns a URL to the generated audio file.

**Authentication Required:** Yes (API Key)

**Request Body:**
```json
{
  "text": "Your text to convert to speech",
  "voice": "en-US-ChristopherNeural",  // Optional, defaults to en-US-ChristopherNeural
  "format": "mp3"                      // Optional, can be mp3 or wav, defaults to mp3
}
```

**Example Response:**
```json
{
  "success": true,
  "file_url": "http://your-domain.com/audio/bc61e862-1a3a-4b8f-b189-cd7b487febc2.mp3",
  "text": "Your text to convert to speech",
  "voice": "en-US-ChristopherNeural",
  "format": "mp3"
}
```

### Get Audio File

```
GET /audio/<filename>
```

Returns the generated audio file for download.

**Example URL:** `/audio/bc61e862-1a3a-4b8f-b189-cd7b487febc2.mp3`

## Authentication

All API endpoints except for the root endpoint require authentication using an API key. You can provide the API key in one of the following ways:

1. In the request header: `X-API-Key: your_api_key_here`
2. As a query parameter: `?api_key=your_api_key_here`

### Setting a Permanent API Key

By default, the API generates a random API key each time the application is started. To set a permanent API key, you need to set the `API_KEY` environment variable before starting the application.

For example:
```bash
# Linux/Mac
export API_KEY=your_secret_api_key
python main.py

# Windows
set API_KEY=your_secret_api_key
python main.py
```

When deploying the application, make sure to configure the `API_KEY` environment variable in your hosting environment.

## Usage Examples

### cURL

Get available voices:
```bash
curl -X GET "http://your-domain.com/api/voices" -H "X-API-Key: your_api_key_here"
```

Convert text to speech:
```bash
curl -X POST "http://your-domain.com/api/tts" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Edge TTS API.",
    "voice": "en-US-ChristopherNeural",
    "format": "mp3"
  }'
```

### Python

```python
import requests
import json

API_URL = "http://your-domain.com"
API_KEY = "your_api_key_here"

# Get available voices
response = requests.get(
    f"{API_URL}/api/voices",
    headers={"X-API-Key": API_KEY}
)
voices = response.json()

# Convert text to speech
response = requests.post(
    f"{API_URL}/api/tts",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "text": "Hello, this is a test of the Edge TTS API.",
        "voice": "en-US-ChristopherNeural",
        "format": "mp3"
    })
)
result = response.json()
audio_url = result["file_url"]

# Download the audio file
audio_response = requests.get(audio_url)
with open("speech.mp3", "wb") as f:
    f.write(audio_response.content)
```

## Notes

- Text length is limited to 5000 characters per request.
- Audio files are stored temporarily and may be deleted periodically, so download and save any files you need to keep.
- When converting speech, use voice names exactly as returned by the `/api/voices` endpoint.
- The API accepts both mp3 and wav format requests for compatibility, but due to limitations in the underlying edge-tts library, all audio is currently generated as MP3 regardless of the requested format.
- Files with a .wav extension will still be MP3 files. If you need actual WAV files, you'll need to convert the MP3 files after downloading.
- The content-type of all audio files will be 'audio/mpeg' regardless of the file extension.