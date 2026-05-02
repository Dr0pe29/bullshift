from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

from groq import Groq

ai_client = Groq()

def check_if_verifiable(sentence):
    """
    Evaluates a sentence and returns 'YES' if it contains a verifiable claim, 
    or 'NO' if it is just an opinion or casual talk.
    """
    prompt = f"""
    You are a binary classification engine for a real-time fact-checking application. 
    Your only job is to determine if a spoken sentence contains a VERIFIABLE factual claim.

    DEFINITION: 
    A verifiable claim is any statement that can be objectively proven TRUE or FALSE by checking reality, history, science, or public records. 

    RULES:
    1. If the sentence contains a verifiable claim (even a false one), output EXACTLY the word: YES
    2. If the sentence is subjective (opinions, feelings), a prediction, a greeting, or casual filler, output EXACTLY the word: NO
    3. Do NOT extract the claim. Do NOT correct the text. Do NOT explain your reasoning. Output ONLY "YES" or "NO".

    EXAMPLES:
    Sentence: "I think tacos are the best food." -> NO
    Sentence: "The Earth is actually flat and sits on a dome." -> YES
    Sentence: "Abraham Lincoln invented the internet." -> YES
    Sentence: "In my opinion, Paris is a very beautiful city." -> NO
    Sentence: "Paris is the capital of Spain." -> YES

    SENTENCE: "{sentence}"
    OUTPUT:
    """
    
    try:
        # THE UPGRADE: 70 Billion parameters of pure logic
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            temperature=0, 
        )
        return response.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f"Groq Error: {e}")
        return "NO"
    

def main():
    try:
        client = DeepgramClient("25bc47fefb8146ab1b4a7b423d4e52112ae37e58")
        dg_connection = client.listen.websocket.v("1")

        # Define what happens when text comes back
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0:
                if result.is_final:
                    print(f"\n They said: {sentence}")
                    print("🔍 Checking if verifiable...")
                    
                    # Call our newly upgraded Groq function
                    is_verifiable = check_if_verifiable(sentence)
                    
                    if "YES" in is_verifiable:
                        # We use the ORIGINAL sentence going forward!
                        print(f"🎯 CLAIM DETECTED: {sentence}")
                        # (Next step: The Fact Check Search!)
                    else:
                        print("⏭️ Ignored (Opinion/Casual)")

                else:
                    # Print interim results on the same line so it looks cool
                    print(f"⏳ {sentence}", end="\r")

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
            endpointing=500,
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