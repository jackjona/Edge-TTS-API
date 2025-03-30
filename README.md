# Edge TTS API

A REST API for Microsoft Edge Text-to-Speech service, providing high-quality text-to-speech conversion with multiple voices and language options.

## API Endpoints

### Root Endpoint

```
GET /
```

Returns basic API information including the API key for authentication.

**Example Response:**
```json
{
  "name": "Edge TTS API",
  "version": "1.0.0",
  "description": "A REST API for Microsoft Edge TTS",
  "endpoints": {
    "voices": "/api/voices",
    "tts": "/api/tts",
    "stream": "/api/stream"
  },
  "demo": "/demo/stream",
  "documentation": "Include X-API-Key header or api_key query parameter with all requests",
  "api_key": "your_api_key_here"
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

Converts text to speech and returns a URL to the generated audio file, or directly downloads the audio file.

**Authentication Required:** Yes (API Key)

**Request Body:**
```json
{
  "text": "Your text to convert to speech",
  "voice": "en-US-ChristopherNeural",  // Optional, defaults to en-US-ChristopherNeural
  "format": "mp3"                      // Optional, can be mp3 or wav, defaults to mp3
}
```

**Query Parameters:**
- `direct`: Set to "true" to directly download the audio file instead of receiving a URL (optional, default: false)

**Standard Response (direct=false):**
```json
{
  "success": true,
  "file_url": "http://your-domain.com/audio/bc61e862-1a3a-4b8f-b189-cd7b487febc2.mp3",
  "text": "Your text to convert to speech",
  "voice": "en-US-ChristopherNeural",
  "format": "mp3"
}
```

**Direct Download Response (direct=true):**
When the `direct` parameter is set to `true`, the API will return the audio file directly as a downloadable attachment instead of a JSON response with a URL.

### Streaming Text-to-Speech

```
POST /api/stream
```

Converts text to speech and streams the audio data directly in real-time without creating a file on the server. This is useful for immediate playback without waiting for the complete file to be generated.

**Authentication Required:** Yes (API Key)

**Request Body:**
```json
{
  "text": "Your text to convert to speech",
  "voice": "en-US-ChristopherNeural",  // Optional, defaults to en-US-ChristopherNeural
  "format": "mp3"                      // Optional, can be mp3 or wav, defaults to mp3
}
```

**Response:**
The API will stream the audio data directly as it's being generated. The response will have the appropriate Content-Type header (audio/mpeg or audio/wav) and can be played immediately or saved to a file.

### Get Audio File

```
GET /audio/<filename>
```

Returns the generated audio file for download.

**Example URL:** `/audio/bc61e862-1a3a-4b8f-b189-cd7b487febc2.mp3`

### Interactive Demo

```
GET /demo/stream
```

An interactive web page that demonstrates the streaming text-to-speech functionality. The demo allows you to:

- Enter text to convert to speech
- Select from available voices
- Choose the audio format (MP3 or WAV)
- Stream and play the generated audio in real-time
- See example code for using the streaming API

## Authentication

All API endpoints except for the root endpoint require authentication using an API key. You can provide the API key in one of the following ways:

1. In the request header: `X-API-Key: your_api_key_here`
2. As a query parameter: `?api_key=your_api_key_here`

## Usage Examples

### cURL

Get available voices:
```bash
curl -X GET "http://your-domain.com/api/voices" -H "X-API-Key: your_api_key_here"
```

Convert text to speech (get URL):
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

Direct download of audio:
```bash
curl -X POST "http://your-domain.com/api/tts?direct=true" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Edge TTS API.",
    "voice": "en-US-ChristopherNeural",
    "format": "mp3"
  }' \
  -o speech.mp3
```

Stream audio in real-time:
```bash
curl -X POST "http://your-domain.com/api/stream" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a streaming test of the Edge TTS API.",
    "voice": "en-US-ChristopherNeural",
    "format": "mp3"
  }' \
  -o streamed_speech.mp3
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

# Example 1: Convert text to speech (get URL and then download)
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

# Download the audio file from the URL
audio_response = requests.get(audio_url)
with open("speech1.mp3", "wb") as f:
    f.write(audio_response.content)

# Example 2: Direct download of audio file
response = requests.post(
    f"{API_URL}/api/tts?direct=true",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "text": "Hello, this is a direct download test of the Edge TTS API.",
        "voice": "en-US-ChristopherNeural",
        "format": "mp3"
    }),
    stream=True  # Important for streaming the binary content
)

# Save the directly downloaded audio file
with open("speech2.mp3", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)

# Example 3: Stream audio in real-time
response = requests.post(
    f"{API_URL}/api/stream",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "text": "Hello, this is a streaming test of the Edge TTS API.",
        "voice": "en-US-ChristopherNeural",
        "format": "mp3"
    }),
    stream=True  # Important for streaming the binary content
)

# Save the streamed audio file or play it in real-time
with open("speech3.mp3", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
            # Optional: Send to audio player for real-time playback
```

## Notes

- Text length is limited to 5000 characters per request.
- Audio files are stored temporarily and will be automatically deleted after 1 hour (configurable via the `AUDIO_MAX_AGE` environment variable in seconds). Download and save any files you need to keep.
- Voice validation is performed to ensure the requested voice exists. Use the names exactly as returned by the `/api/voices` endpoint.
- Only mp3 and wav formats are currently supported.
- The streaming endpoint (/api/stream) offers several advantages:
  - Immediate playback: Audio begins playing as soon as the first chunks are generated, without waiting for the entire file
  - Reduced server load: No temporary files are stored on the server
  - Lower latency: Users experience faster response times for audio playback
  - Better for real-time applications: Ideal for chat bots, voice assistants, and interactive applications

## Configuration (Environment Variables)

The API can be configured using the following environment variables:

- `API_KEY`: API key for authentication (default: "edge_tts_api_key_12345")
- `DEBUG`: Enable debug mode (default: "True")
- `HOST`: Host to bind the server to (default: "0.0.0.0")
- `PORT`: Port to bind the server to (default: 5000)
- `AUDIO_FOLDER_NAME`: Name of the folder where audio files are stored (default: "edge_tts_audio")
- `AUDIO_MAX_AGE`: Maximum age of audio files in seconds before they are deleted (default: 3600 - 1 hour)