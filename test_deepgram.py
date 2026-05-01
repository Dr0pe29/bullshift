from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

def main():
    try:
        client = DeepgramClient("APIKEYHERE")
        dg_connection = client.listen.websocket.v("1")

        # Define what happens when text comes back
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0:
                # If it's the final sentence, print it in Green
                if result.is_final:
                    print(f"✅ FINAL: {sentence}")
                # If it's still guessing the words, print it with an hourglass
                else:
                    print(f"⏳ Interim: {sentence}")

        def on_error(self, error, **kwargs):
            print(f"❌ Error: {error}")

        # Bind the events
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        # THE FIX IS HERE: Force the exact format and turn on Interim Results
        options = LiveOptions(
            model="nova-3",
            language="en",
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

        # Start the microphone with your specific Index
        MIC_INDEX = 1  # <--- CHANGE THIS TO YOUR MIC INDEX!
        
        print("🟢 Connected! Start talking (Press Ctrl+C to stop)...")
        microphone = Microphone(dg_connection.send, input_device_index=MIC_INDEX)
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