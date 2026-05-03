import os
import json
import asyncio
import threading
import time

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from check_verifiable import analyze_verifiability
from fact_checker import analyze_transcript

# Choose fact-checker backend ("ddgs" or "tavily")
fact_checker_backend = os.getenv("FACT_CHECKER_BACKEND", "ddgs").lower()
if fact_checker_backend == "tavily":
    from fact_checker_tavily import fact_check_claim
else:
    from fact_checker_unlimited import fact_check_claim

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
deepgram_stop_event = None


class TranscriptRequest(BaseModel):
    transcript: str


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

def fact_check_and_broadcast(sentence):
    try:
        print("🔍 Checking if verifiable...")

        verifiable = analyze_verifiability(sentence)

        if verifiable["label"] == "YES":
            claim_to_check = verifiable.get("cleaned_claim") or sentence
            print(f"🎯 CLAIM DETECTED: {claim_to_check}")

            analysis = fact_check_claim(claim_to_check)

            print(f"\n{analysis['raw_response']}\n")
            print("Listening...")

            broadcast_from_thread({
                "type": "fact",
                "status": "claim_detected",
                "text": sentence,
                "cleaned_text": claim_to_check,
                "verdict": analysis["raw_response"],
                "verifiable": True,
                "confidence": analysis["confidence"],
                "justification": analysis["justification"],
                "evidence_snippets": analysis["evidence_snippets"],
            })

        elif verifiable["label"] == "NO_CONTEXT":
            print(f"🤷 NO CONTEXT: '{sentence}'")
            print("Listening...")

        else:
            print(f"⏭️ Ignored: '{sentence}'")
            print("Listening...")

    except Exception as e:
        print(f"❌ Fact-check error: {e}")

        broadcast_from_thread({
            "type": "error",
            "text": str(e),
        })

# ===============================
# DEEPGRAM MICROPHONE LOGIC
# ===============================
def start_deepgram_microphone(stop_event):
    microphone = None
    dg_connection = None

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
                if result.is_final:
                    print(f"✅ FINAL: {sentence}")

                    broadcast_from_thread({
                        "type": "final",
                        "text": sentence,
                    })

                    threading.Thread(
                        target=fact_check_and_broadcast,
                        args=(sentence,),
                        daemon=True
                    ).start()
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

        # Back to standard configurations
        options = LiveOptions(
            model="nova-3",
            language="en",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            endpointing=3000,
        )

        print("Connecting to Deepgram...")
        if dg_connection.start(options) is False:
            print("Failed to connect.")
            return

        
        print("🟢 Connected! Start talking (Press Ctrl+C to stop)...")
        microphone = Microphone(dg_connection.send, input_device_index=MIC_INDEX)
        microphone.start()

        while not stop_event.is_set():
            time.sleep(1)

    except Exception as e:
        print(f"Could not open socket: {e}")

    finally:
        print("🛑 Stopping Deepgram microphone...")

        if microphone:
            microphone.finish()

        if dg_connection:
            dg_connection.finish()

        print("Stopped recording.")


# ===============================
# ROUTES
# ===============================

@app.get("/")
def health_check():
    return {
        "status": "backend running",
    }


@app.post("/transcript/analyze")
def analyze_full_transcript(payload: TranscriptRequest):
    return analyze_transcript(payload.transcript)


@app.websocket("/ws/transcript")
async def transcript_websocket(websocket: WebSocket):
    global main_event_loop
    global deepgram_thread_started
    global deepgram_stop_event

    await websocket.accept()
    connected_clients.add(websocket)

    main_event_loop = asyncio.get_running_loop()

    if not deepgram_thread_started:
        deepgram_thread_started = True
        deepgram_stop_event = threading.Event()

        thread = threading.Thread(
            target=start_deepgram_microphone,
            args=(deepgram_stop_event,),
            daemon=True,
        )
        thread.start()

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.discard(websocket)

        if len(connected_clients) == 0:
            if deepgram_stop_event:
                deepgram_stop_event.set()

            deepgram_thread_started = False
            deepgram_stop_event = None

            print("No clients connected. Requested Deepgram stop.")
