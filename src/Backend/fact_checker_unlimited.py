from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS 
import re

# Load environment variables
load_dotenv()

# Initialize AI Client
ai_client = Groq()


def _parse_confidence_response(response_text):
    match = re.search(r"CONFIDENCE:\s*(\d+(?:\.\d+)?)%?\s*\|\s*(.*)", response_text, re.IGNORECASE | re.DOTALL)

    if not match:
        return None, response_text.strip()

    confidence = float(match.group(1))
    justification = match.group(2).strip()

    return confidence, justification

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
        evidence_snippets = [res.get("body", "") for res in search_results if res.get("body")]
        web_context = "\n".join([f"- {snippet}" for snippet in evidence_snippets])
        
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
        response_text = response.choices[0].message.content.strip()
        confidence, justification = _parse_confidence_response(response_text)

        return {
            "confidence": confidence,
            "justification": justification,
            "raw_response": response_text,
            "evidence_snippets": evidence_snippets,
        }
        
    except Exception as e:
        return {
            "confidence": None,
            "justification": f"Analysis failed: {e}",
            "raw_response": f"❌ ERROR | Analysis failed: {e}",
            "evidence_snippets": [],
        }

# Example Usage:
# print(fact_check_claim("The moon is made of green cheese"))