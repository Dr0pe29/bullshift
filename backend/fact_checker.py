import os
import requests
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Initialize AI and Search Clients
ai_client = Groq()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def hybrid_fact_check(claim):
    """
    WATERFALL ARCHITECTURE:
    1. Tries the human-verified Google Fact Check API first.
    2. If no human review exists, falls back to Tavily AI Search + Groq 70B.
    """
    print(f"\n🌍 Checking Tier 1 (Human Database) for: '{claim}'...")
    
    # ==========================================
    # TIER 1: GOOGLE FACT CHECK API
    # ==========================================
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={claim}&key={google_key}"
        try:
            response = requests.get(url).json()
            
            # If human fact-checkers have reviewed this:
            if "claims" in response and len(response["claims"]) > 0:
                first_match = response["claims"][0]
                reviewer = first_match["claimReview"][0]["publisher"]["name"]
                verdict = first_match["claimReview"][0]["textualRating"]
                
                return f"🏛️ HUMAN VERIFIED by {reviewer}: [{verdict.upper()}]"
        except Exception as e:
            print(f"Google API Error: {e}")

    # ==========================================
    # TIER 2: TAVILY RAG FALLBACK
    # ==========================================
    print(f"🤖 No human review found. Searching Tavily AI...")
    
    try:
        # Search Tavily (search_depth="basic" is incredibly fast)
        search_result = tavily_client.search(query=claim, search_depth="basic", max_results=3)
        
        # Extract the high-quality content summaries from the results
        web_context = "\n".join([f"- {res['content']}" for res in search_result.get('results', [])])
        
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
        
        # Use your massive 70B model to judge the Tavily results
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            temperature=0, 
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"ERROR | Web fallback failed: {e}"