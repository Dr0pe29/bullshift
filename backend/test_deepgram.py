import os
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from check_verifiable import check_if_verifiable
from fact_checker_unlimited import fact_check_claim

def main():
    try:
        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        client = DeepgramClient(deepgram_key)
        dg_connection = client.listen.websocket.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript.strip()
            
            if len(sentence) > 0:
                if result.is_final:
                    print(f"\n🔍 Checking if verifiable...")
                    
                    # Evaluate the isolated sentence immediately
                    is_verifiable = check_if_verifiable(sentence)
                    
                    if "YES" in is_verifiable:
                        print(f"🎯 CLAIM DETECTED: {sentence}")
                        verdict = fact_check_claim(sentence)
                        print(f"\n{verdict}\n")
                        print("Listening...")
                        
                    elif "NO_CONTEXT" in is_verifiable:
                        print(f"🤷 NO CONTEXT: '{sentence}' (Too vague to check)")
                        print("Listening...")
                        
                    else:
                        print(f"⏭️ Ignored: '{sentence}'")
                        print("Listening...")
                        
                else:
                    # Print interim results on the same line so it feels alive
                    print(f"🗣️ {sentence}", end="\r")

        def on_error(self, error, **kwargs):
            # Intercept and ignore the noisy "ConnectionClosed" error during shutdown
            if "ConnectionClosed" in str(error):
                return
            print(f"❌ Error: {error}")

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
            # Removed the 3000ms delay so it evaluates quickly!
        )

        print("Connecting to Deepgram...")
        if dg_connection.start(options) is False:
            print("Failed to connect.")
            return

        # Start the microphone (Add your specific input_device_index if needed)
        print("🟢 Connected! Start talking (Press Ctrl+C to stop)...")
        microphone = Microphone(dg_connection.send)
        microphone.start()

        # Keep the script running
        input("Press Enter to stop recording...\n\n")

        # Cleanup
        microphone.finish()
        dg_connection.finish()
        print("Stopped recording.")

    except Exception as e:
        print(f"Could not open socket: {e}")

if __name__ == "__main__":
    main()