import os
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from check_verifiable import check_if_verifiable
from fact_checker_unlimited import fact_check_claim # <-- Bring back the fast checker
from multi_agent import run_courtroom               # <-- Keep the deep courtroom

def main():
    try:
        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        client = DeepgramClient(deepgram_key)
        dg_connection = client.listen.websocket.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript.strip()
            
            if len(sentence) > 0:
                if result.is_final:
                    print(f"\n  Checking if verifiable...")
                    
                    is_verifiable = check_if_verifiable(sentence)
                    
                    if "YES" in is_verifiable:
                        print(f"\n🚨 CLAIM DETECTED: {sentence}")
                        
                        # ==========================================
                        # 1. THE QUICK FIRST GUESS
                        # ==========================================
                        print("⚡ Fetching quick initial verdict...")
                        quick_verdict = fact_check_claim(sentence)
                        print(f"   > {quick_verdict}\n")
                        
                        # ==========================================
                        # 2. THE DEEP MULTI-AGENT ANALYSIS
                        # ==========================================
                        #print("🏛️ Escalating to the Multi-Agent Courtroom for deep analysis...")
                        #run_courtroom(sentence) 
                        
                        print("\nListening...")
                        
                    elif "NO_CONTEXT" in is_verifiable:
                        print(f"  NO CONTEXT: '{sentence}' (Too vague to check)")
                        print("Listening...")
                        
                    else:
                        print(f"  Ignored: '{sentence}'")
                        print("Listening...")
                        
                else:
                    print(f"  {sentence}", end="\r")

        def on_error(self, error, **kwargs):
            if "ConnectionClosed" in str(error):
                return
            print(f"  Error: {error}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

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

        print("  Connected! Start talking (Press Ctrl+C to stop)...")
        microphone = Microphone(dg_connection.send)
        microphone.start()

        input("Press Enter to stop recording...\n\n")

        microphone.finish()
        dg_connection.finish()
        print("Stopped recording.")

    except Exception as e:
        print(f"Could not open socket: {e}")

if __name__ == "__main__":
    main()