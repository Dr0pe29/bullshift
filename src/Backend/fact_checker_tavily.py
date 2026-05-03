from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import re
import os

# Load environment variables
load_dotenv()

# Initialize AI Client
ai_client = Groq()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def _parse_confidence_response(response_text):
    """Parse confidence score from response. Tries multiple patterns for robustness."""
    if not response_text:
        return None, response_text.strip()
    
    # Try primary format: CONFIDENCE: [X]% | explanation
    match = re.search(r"CONFIDENCE:\s*(\d+(?:\.\d+)?)%?\s*\|\s*(.*)", response_text, re.IGNORECASE | re.DOTALL)
    if match:
        try:
            confidence = float(match.group(1))
            justification = match.group(2).strip()
            return confidence, justification
        except (ValueError, IndexError):
            pass
    
    # Try alternate format: [X]% or just a number
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", response_text)
    if match:
        try:
            confidence = float(match.group(1))
            justification = response_text.strip()
            return confidence, justification
        except (ValueError, IndexError):
            pass
    
    # If no score found, return None
    return None, response_text.strip()


def _extract_sources(search_results):
    """Extract sources from Tavily search results."""
    sources = []

    for result in search_results:
        title = (result.get("title") or "").strip()
        url = (result.get("url") or "").strip()
        content = (result.get("content") or "").strip()

        if title and url:
            sources.append(f"{title} - {url}")
        elif url:
            sources.append(url)
        elif title:
            sources.append(title)
        elif content:
            sources.append(content[:100])  # First 100 chars of content

    return sources


def _search_with_fallback(claim):
    """
    Search using Tavily with fallback strategies.
    Returns search results with retry logic and query refinement.
    """
    try:
        # First try: exact claim
        response = tavily_client.search(claim, max_results=5, include_answer=True)
        results = response.get("results", [])
        
        if results and len(results) >= 2:
            return results
    except Exception as e:
        print(f"  Search attempt 1 failed: {e}")
    
    # Fallback: try a shorter, simplified version of the claim
    try:
        simplified = re.sub(r"\b(is|are|was|were|the|a|an|and|or)\b", "", claim, flags=re.IGNORECASE).strip()
        simplified = " ".join(simplified.split()[:8])  # First 8 words
        
        if simplified and len(simplified) > 5:
            response = tavily_client.search(simplified, max_results=5, include_answer=True)
            results = response.get("results", [])
            
            if results and len(results) >= 1:
                return results
    except Exception as e:
        print(f"  Search attempt 2 failed: {e}")
    
    # If all fails, return empty list
    return []


def fact_check_claim(claim):
    """
    IMPROVED FACT-CHECKING with TAVILY RAG:
    Uses Tavily search with fallback, nuanced confidence scoring, and better calibration.
    """
    print(f"\n🌍 Analyzing confidence for: '{claim}'...")
    
    try:
        # 1. Search with fallback strategy using Tavily
        search_results = _search_with_fallback(claim)
        
        if not search_results:
            return {
                "confidence": 50,  # Neutral if no context found
                "justification": "No web context available. Claim cannot be verified.",
                "raw_response": "📊 CONFIDENCE: 50% | No web context found.",
                "evidence_snippets": [],
                "sources": [],
            }
        
        # 2. Extract evidence (Tavily uses "content" field instead of "body")
        evidence_snippets = [res.get("content", "") for res in search_results if res.get("content")]
        sources = _extract_sources(search_results)
        web_context = "\n".join([f"- {snippet}" for snippet in evidence_snippets[:5]])
        
        # 3. Improved prompt for nuanced scoring
        prompt = f"""
        You are a high-precision fact-checking validator. Evaluate the likelihood that the CLAIM is objectively true based ONLY on the provided WEB CONTEXT.

        CLAIM: "{claim}"

        WEB CONTEXT:
        {web_context}

        SCORING GUIDELINES:
        - 95-100%: Overwhelming consensus, multiple authoritative sources confirm.
        - 80-94%: Strong evidence supports the claim with minimal conflicting information.
        - 65-79%: Good evidence supports the claim, but some nuance or caveats exist.
        - 50-64%: Conflicting evidence or inconclusive. Equal weight to true/false.
        - 35-49%: Evidence leans against the claim, but not definitive.
        - 20-34%: Strong evidence contradicts the claim.
        - 0-19%: Overwhelming evidence shows the claim is false.

        OUTPUT FORMAT: 📊 CONFIDENCE: [X]% | [Detailed explanation of evidence found and reasoning]

        Be specific and calibrated. Avoid clustering at extremes. Use the full 0-100 range."""
        
        # 4. Call the API with better model selection
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,  # Slightly higher than 0 for more variability
        )
        response_text = response.choices[0].message.content.strip()
        confidence, justification = _parse_confidence_response(response_text)
        
        # If parsing failed, assign neutral score
        if confidence is None:
            confidence = 50
            justification = response_text[:200]
        
        # Clamp to valid range
        confidence = max(0, min(100, confidence))

        return {
            "confidence": confidence,
            "justification": justification,
            "raw_response": response_text,
            "evidence_snippets": evidence_snippets,
            "sources": sources,
        }
        
    except Exception as e:
        print(f"Fact-check error: {e}")
        return {
            "confidence": None,
            "justification": f"Analysis failed: {e}",
            "raw_response": f"❌ ERROR | Analysis failed: {e}",
            "evidence_snippets": [],
            "sources": [],
        }


# Example Usage:
# print(fact_check_claim("The moon is made of green cheese"))
