import os
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
    Scrapes the live web via DuckDuckGo and feeds the context to Groq 70B.
    """
    print(f"\n🌍 Searching the web for: '{claim}'...")
    
    try:
        # 1. Scrape the top 3 results using the DDGS library
        search_results = DDGS().text(claim, max_results=3)
        
        # 2. Extract the snippet text from the search results
        web_context = "\n".join([f"- {res['body']}" for res in search_results])
        
        # 3. Build the ruthless Judge prompt
        prompt = f"""
        You are a ruthless fact-checking AI. 
        Determine if the spoken CLAIM is TRUE, FALSE, MIXED, or INCONCLUSIVE based ONLY on the provided WEB CONTEXT.

        CLAIM: "{claim}"

        WEB CONTEXT:
        {web_context}

        RULES:
        1. Output your response in this EXACT format: 🌐 AI VERDICT: [TRUE/FALSE/MIXED] | [One short sentence explaining why].
        2. Do not add any conversational filler. Be brutal and direct.

        OUTPUT:
        """
        
        # 4. Use your massive 70B model to judge the DuckDuckGo results
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0, 
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ ERROR | Web search failed: {e}"