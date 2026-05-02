import os
import json
import asyncio
import threading
import time

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
MIC_INDEX = int(os.getenv("MIC_INDEX", "1"))
DEEPGRAM_LANGUAGE = os.getenv("DEEPGRAM_LANGUAGE", "en")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# WEBSOCKET STATE
# ===============================
connected_clients = set()
main_event_loop = None
deepgram_thread_started = False


# ===============================
# WEBSOCKET HELPERS
# ===============================
async def broadcast_message(message):
    disconnected_clients = []

    for websocket in connected_clients:
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            disconnected_clients.append(websocket)

    for websocket in disconnected_clients:
        connected_clients.discard(websocket)


def broadcast_from_thread(message):
    if main_event_loop is None:
        return

    asyncio.run_coroutine_threadsafe(
        broadcast_message(message),
        main_event_loop,
    )

# ===============================
# DEEPGRAM MICROPHONE LOGIC
# ===============================
def start_deepgram_microphone():
    try:

        if not DEEPGRAM_API_KEY:
            print("Error: Missing DEEPGRAM_API_KEY in .env")
            return
        
        client = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = client.listen.websocket.v("1")

        # Define what happens when text comes back
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0:
                # If it's the final sentence, print it in Green
                if result.is_final:
                    print(f"✅ FINAL: {sentence}")

                    broadcast_from_thread({
                        "type": "final",
                        "text": sentence,
                    })
                # If it's still guessing the words, print it with an hourglass
                else:
                    print(f"⏳ Interim: {sentence}")
                    broadcast_from_thread({
                        "type": "interim",
                        "text": sentence,
                    })

        def on_error(self, error, **kwargs):
            print(f"❌ Error: {error}")
            broadcast_from_thread({
                "type": "error",
                "text": str(error),
            })

        # Bind the events
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        # Force the exact format and turn on Interim Results
        options = LiveOptions(
            model="nova-3",
            language=DEEPGRAM_LANGUAGE,
            smart_format=True,
            encoding="linear16",    # Match the local test
            channels=1,             # Match the local test
            sample_rate=16000,      # Match the local test
            interim_results=True,   # STREAM THE WORDS INSTANTLY
        )

        print("Connecting to Deepgram...")
        if dg_connection.start(options) is False:
            print("Failed to connect.")
            return

        
        print("🟢 Connected! Start talking (Press Ctrl+C to stop)...")
        microphone = Microphone(dg_connection.send, input_device_index=MIC_INDEX)
        microphone.start()

        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Could not open socket: {e}")


# ===============================
# ROUTES
# ===============================

@app.get("/")
def health_check():
    return {
        "status": "backend running",
    }


@app.websocket("/ws/transcript")
async def transcript_websocket(websocket: WebSocket):
    global main_event_loop
    global deepgram_thread_started

    await websocket.accept()
    connected_clients.add(websocket)

    main_event_loop = asyncio.get_running_loop()

    if not deepgram_thread_started:
        deepgram_thread_started = True

        thread = threading.Thread(
            target=start_deepgram_microphone,
            daemon=True,
        )
        thread.start()

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
