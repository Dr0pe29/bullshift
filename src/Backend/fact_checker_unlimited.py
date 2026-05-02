from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS 

# Load environment variables
load_dotenv()

# Initialize AI Client
ai_client = Groq()

def fact_check_claim(claim):
    """
    SINGLE-TIER ARCHITECTURE:
    Calculates a confidence percentage based on live web context.
    """
    print(f"\n🌍 Analyzing confidence for: '{claim}'...")
    
    try:
        # 1. Scrape the top 3 results
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(claim, max_results=3)]
        
        # 2. Extract the snippet text
        web_context = "\n".join([f"- {res['body']}" for res in search_results])
        
        # 3. Build the Probabilistic Judge prompt
        prompt = f"""
        You are a high-precision fact-checking validator. 
        Evaluate the likelihood that the CLAIM is objectively true based ONLY on the provided WEB CONTEXT.

        CLAIM: "{claim}"

        WEB CONTEXT:
        {web_context}

        RULES:
        1. Assign a CONFIDENCE SCORE from 0% to 100%.
           - 100%: Absolute factual certainty.
           - 50%: Conflicting evidence or equal weight to true/false.
           - 0%: Proven completely false.
        2. Output your response in this EXACT format: 📊 CONFIDENCE: [X]% | [Brief technical justification].
        3. Do not use conversational filler. Be objective and precise.

        OUTPUT:
        """
        
        # 4. Use the 8B model for better nuance and calibration
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0, # Keep temp at 0 for consistency in scoring
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ ERROR | Analysis failed: {e}"

# Example Usage:
# print(fact_check_claim("The moon is made of green cheese"))