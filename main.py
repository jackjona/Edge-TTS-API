from app import app, HOST, PORT, DEBUG, API_KEY
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

if __name__ == "__main__":
    # Print API information
    print(f"Edge TTS API running at http://{HOST}:{PORT}")
    print(f"API Key: {API_KEY}")
    print(f"Debug mode: {'Enabled' if DEBUG else 'Disabled'}")
    
    # Run the application
    app.run(host=HOST, port=PORT, debug=DEBUG)
