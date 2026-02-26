import os
import base64
import asyncio
import pyaudio
import concurrent.futures
from openai import AsyncOpenAI


# Audio hardware constants required by the API
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
CHUNK = 2048


def get_env_variables():
    """Retrieves necessary configuration from environment variables and validates them."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if endpoint is None:
        raise RuntimeError(
            "Missing environment variable 'AZURE_OPENAI_ENDPOINT'. "
            "Please set it to your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com)."
        )
    base_url = endpoint.replace("https://", "wss://").rstrip("/") + "/openai/v1"

    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    if deployment_name is None:
        raise RuntimeError(
            "Missing environment variable 'AZURE_OPENAI_DEPLOYMENT_NAME'. "
            "Please set it to the name of your Azure OpenAI deployment."
        )

    token = os.getenv("AZURE_OPENAI_API_KEY")
    if token is None:
        raise RuntimeError(
            "Missing environment variable 'AZURE_OPENAI_API_KEY'. "
            "Please set it to a valid Azure OpenAI API key."
        )
        
    return base_url, deployment_name, token


def get_session_config():
    """Defines the session configuration for the real-time audio interaction."""
    return {
        "type": "realtime",
        "instructions": "You are a helpful assistant. You respond only by voice.",
        "output_modalities": ["audio"],
        "audio": {
            "input": {
                "format": {
                    "type": "audio/pcm",
                    "rate": RATE
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200,
                    "create_response": True
                }
            },
            "output": {
                "voice": "alloy",
                "format": {
                    "type": "audio/pcm",
                    "rate": RATE
                }
            }
        }
    }


async def send_audio(connection, mic_stream, pool):
    """Reads raw PCM data from the microphone and streams it to the model."""
    loop = asyncio.get_event_loop()
    try:
        while True:
            # The executor prevents the blocking audio read from halting the async loop
            data = await loop.run_in_executor(pool, mic_stream.read, CHUNK, False)
            base64_audio = base64.b64encode(data).decode("utf-8")
            await connection.input_audio_buffer.append(audio=base64_audio)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Microphone error: {e}")


async def receive_events(connection, speaker_stream, pool):
    """Listens for server events, prints transcripts, and plays audio chunks."""
    loop = asyncio.get_event_loop()
    try:
        async for event in connection:
            if event.type == "session.created":
                print(f"Session ID: {event.session.id}")
            elif event.type == "response.output_audio_transcript.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_audio.delta":
                audio_data = base64.b64decode(event.delta)
                await loop.run_in_executor(pool, speaker_stream.write, audio_data)
            elif event.type == "response.output_audio_transcript.done":
                print() 
            elif event.type == "error":
                print("\nReceived an error event.")
                print(f"Error code: {event.error.code}")
                print(f"Error message: {event.error.message}")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Speaker error: {e}")


async def main() -> None:
    """Sets up audio streams, connects to the model, and manages concurrent send/receive tasks."""
    p = pyaudio.PyAudio()
    
    # Initialize separate streams for input (mic) and output (speaker)
    mic_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    speaker_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
    
    try:
        base_url, deployment_name, token = get_env_variables()

        client = AsyncOpenAI(websocket_base_url=base_url, api_key=token)

        # Manage threads for blocking operations
        with concurrent.futures.ThreadPoolExecutor() as pool:
            async with client.realtime.connect(model=deployment_name) as connection:
                # session configuration with flat keys
                await connection.session.update(session=get_session_config())

                print("Connection established. Speak into your microphone. Press Ctrl+C to stop.")

                # Schedule both tasks to run concurrently
                send_task = asyncio.create_task(send_audio(connection, mic_stream, pool))
                receive_task = asyncio.create_task(receive_events(connection, speaker_stream, pool))

                # Keep the loop running until both tasks complete or are interrupted
                await asyncio.gather(send_task, receive_task, return_exceptions=True)
    finally:
        if mic_stream is not None:
            mic_stream.stop_stream()
            mic_stream.close()
        if speaker_stream is not None:
            speaker_stream.stop_stream()
            speaker_stream.close()
        if p is not None:
            p.terminate()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")