import os
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Initialize Cloud Clients
ai_client = Groq()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

FAST_MODEL = "llama-3.1-8b-instant"
#JUDGE_MODEL = "llama-3.3-70b-versatile"
JUDGE_MODEL = "llama-3.1-8b-instant"

def researcher_agent(claim):
    """Agent 1: Scours the web using Tavily and summarizes the facts."""
    print(f"\n[🧑‍🔬 RESEARCHER] Investigating claim: '{claim}'...")
    
    try:
        search_result = tavily_client.search(query=claim, search_depth="basic", max_results=3)
        web_context = "\n".join([f"- {res['content']}" for res in search_result.get('results', [])])
        
        prompt = f"""
        You are a factual Researcher. Summarize the following web context regarding this claim: "{claim}"
        Keep it purely factual and objective. Do not issue a true/false judgment yet.
        
        WEB CONTEXT:
        {web_context}
        """
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=FAST_MODEL,
            temperature=0,
        )
        summary = response.choices[0].message.content.strip()
        print(f"[🧑‍🔬 RESEARCHER] Context gathered. Handing off to the Critic...")
        return summary
    
    except Exception as e:
        return f"Error gathering research: {e}"

def critic_agent(claim, research_summary):
    """Agent 2: Tries to poke holes in the Researcher's data."""
    print(f"[🕵️ CRITIC] Analyzing research for bias and missing context...")
    
    prompt = f"""
    You are a skeptical Critic playing Devil's Advocate. 
    Read the CLAIM and the RESEARCH SUMMARY below. 
    Your job is to point out missing context, potential bias, logical fallacies, or weak evidence in the research.
    Be brutal, concise, and cynical. Do not issue a final true/false verdict yourself.
    
    CLAIM: "{claim}"
    
    RESEARCH SUMMARY:
    {research_summary}
    """
    
    response = ai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=FAST_MODEL,
        temperature=0.5, 
    )
    critique = response.choices[0].message.content.strip()
    print(f"[🕵️ CRITIC] Flaws identified. Passing case to the Judge...")
    return critique

def judge_agent(claim, research_summary, critique):
    """Agent 3: Weighs the evidence and issues the final verdict WITH score and sources."""
    print(f"[👨‍⚖️ JUDGE] Weighing the evidence and extracting key facts...")
    
    prompt = f"""
    You are the final Judge in a fact-checking courtroom.
    Evaluate the spoken CLAIM based on the RESEARCH SUMMARY and the CRITIC'S PUSHBACK.
    
    CLAIM: "{claim}"
    
    RESEARCH SUMMARY:
    {research_summary}
    
    CRITIC'S PUSHBACK:
    {critique}
    
    RULES:
    1. You must format your exact output like this:
       [VERDICT] | [SCORE]% | [JUSTIFICATION] | [KEY_FACTS]
    2. [VERDICT] must be exactly one of: TRUE, FALSE, MIXED, or INCONCLUSIVE.
    3. [SCORE] must be a number between 0 and 100 representing your confidence.
    4. [JUSTIFICATION] must be a 2-3 sentence explanation of your ruling.
    5. [KEY_FACTS] must be a short, bulleted list (using dashes) of the 1-2 most critical facts or sources from the RESEARCH SUMMARY that drove your decision.
    """
    
    response = ai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=JUDGE_MODEL,
        temperature=0, 
    )
    return response.choices[0].message.content.strip()

def run_courtroom(claim):
    """Orchestrates the pipeline between the three agents."""
    print("\n" + "="*60)
    print("🏛️  STARTING MULTI-AGENT FACT CHECK")
    print("="*60)
    
    research_data = researcher_agent(claim)
    critic_data = critic_agent(claim, research_data)
    raw_verdict = judge_agent(claim, research_data, critic_data)
    
    # Split the Judge's response into 4 parts now
    try:
        verdict_parts = raw_verdict.split("|")
        verdict_status = verdict_parts[0].strip()
        confidence = verdict_parts[1].strip()
        justification = verdict_parts[2].strip()
        # Grab the 4th part if it exists
        key_facts = verdict_parts[3].strip() if len(verdict_parts) > 3 else "No specific facts cited."
    except:
        verdict_status = "ERROR"
        confidence = "N/A"
        justification = raw_verdict
        key_facts = "Parse Error"

    print("\n" + "="*60)
    print("📜 COURTROOM LOGS")
    print("="*60)
    print(f"🗣️ CLAIM: {claim}\n")
    print(f"--- 🧑‍🔬 RESEARCHER ---\n{research_data}\n")
    print(f"--- 🕵️ CRITIC ---\n{critic_data}\n")
    print(f"--- 👨‍⚖️ THE VERDICT ---")
    print(f"STATUS:     {verdict_status}")
    print(f"CONFIDENCE: {confidence}")
    print(f"REASONING:  {justification}")
    print(f"KEY FACTS:\n  {key_facts.replace('- ', '  - ')}") # Indent the bullets nicely
    print("="*60 + "\n")
    
    return raw_verdict

# Quick test
if __name__ == "__main__":
    test_claim = "Napoleon Bonaparte was extremely short for his time."
    run_courtroom(test_claim)