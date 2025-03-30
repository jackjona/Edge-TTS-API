import asyncio
import edge_tts

async def test_mp3():
    communicate = edge_tts.Communicate("This is a test of mp3 format.", "en-US-ChristopherNeural")
    await communicate.save("test_mp3.mp3")
    print("MP3 file saved successfully")

async def test_wav():
    communicate = edge_tts.Communicate("This is a test of wav format.", "en-US-ChristopherNeural")
    await communicate.save("test_wav.wav")
    print("WAV file saved successfully")

async def main():
    print("Testing MP3 format...")
    await test_mp3()
    
    print("\nTesting WAV format...")
    await test_wav()

if __name__ == "__main__":
    asyncio.run(main())