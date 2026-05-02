from dotenv import load_dotenv
from groq import Groq

load_dotenv()
ai_client = Groq()

def check_if_verifiable(sentence):
    """
    Returns 'YES' if the sentence is a full claim.
    Returns 'NO_CONTEXT' if it's a fragment or uses vague pronouns.
    Returns 'NO' if it's casual conversation or an opinion.
    """
    prompt = f"""
    You are a precision classification engine for a real-time fact-checking application. 
    Your objective is to evaluate a spoken sentence and categorize it into EXACTLY one of THREE categories: YES, NO, or NO_CONTEXT.

    RULES:
    1. YES (Verifiable Claim): The sentence is a complete assertion that can be objectively proven TRUE or FALSE through evidence. It contains a clear subject and claims a specific fact, event, or status. 
    - Note: Claims about a current or absolute status (e.g., "Portugal is the world champion", "Water is wet") are YES, even if they lack a specific date or location.
    - Note: The statement does not have to be true to be a YES; it just has to be verifiable.
    2. NO (Non-Claim): The sentence cannot be fact-checked. This includes subjective opinions, feelings, predictions about the future, questions, commands, greetings, or casual conversational filler.
    3. NO_CONTEXT (Unresolved): The sentence is an incomplete fragment or relies on unresolved pronouns/demonstratives ("he", "she", "they", "it", "this", "that") making the specific subject impossible to identify without prior conversation.

    Do NOT explain your reasoning. Output EXACTLY one of the three keywords.

    EXAMPLES:
    Sentence: "I think tacos are the best food." -> NO
    Sentence: "France won." -> NO_CONTEXT
    Sentence: "France won the 1998 FIFA World Cup." -> YES
    Sentence: "He invented the internet." -> NO_CONTEXT
    Sentence: "Abraham Lincoln invented the internet." -> YES
    Sentence: "Portugal are world champion in football." -> YES
    Sentence: "They are the reigning champions." -> NO_CONTEXT
    Sentence: "It will probably rain tomorrow." -> NO
    Sentence: "The inflation rate dropped by two percent last month." -> YES

    SENTENCE: "{sentence}"
    OUTPUT:
    """
    
    try:
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0,
        )
        return response.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f"Groq Error: {e}")
        return "NO"