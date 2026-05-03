from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()
ai_client = Groq()


_LABEL_PATTERN = re.compile(r"\b(YES|NO|NO_CONTEXT)\b", re.IGNORECASE)
_QUESTION_PATTERN = re.compile(r"^(what|who|when|where|why|how|is|are|do|does|did|can|could|would|should|will|won't|isn't|aren't|don't|doesn't|didn't)\b", re.IGNORECASE)
_LEAD_IN_PATTERNS = [
    r"^it'?s common sense that\s+",
    r"^everyone knows that\s+",
    r"^everybody knows that\s+",
    r"^did you know that\s+",
    r"^do you know that\s+",
    r"^you know that\s+",
    r"^people say that\s+",
    r"^the truth is that\s+",
    r"^i (?:think|believe|guess|feel) that\s+",
    r"^i (?:think|believe|guess|feel)\s+",
    r"^in my opinion,?\s*",
    r"^obviously,?\s*",
    r"^honestly,?\s*",
    r"^to be honest,?\s*",
    r"^dude,?\s*",
    r"^bro,?\s*",
    r"^man,?\s*",
]
_NON_VERIFIABLE_PREFIXES = (
    "hi", "hello", "hey", "thanks", "thank you", "please", "ok", "okay"
)
_SUBJECTIVE_VALUE_PATTERNS = (
    r"\b(best|worst|better|worse|good|bad|amazing|awesome|terrible|great|awful|nice|boring|interesting|beautiful|ugly)\b",
    r"\b(better than|worse than|more important than|less important than|more popular than|less popular than)\b",
    r"\b(one of the best|the best|the worst|the greatest|the worst)\b",
    r"\b(good for|bad for|good to|bad to|good at|bad at)\b",
)
_NO_CONTEXT_PREFIXES = (
    "he ", "she ", "they ", "it ", "this ", "that ", "these ", "those "
)


_FACTUAL_ASSERTION_PATTERN = re.compile(
    r"\b(\d{2,4}|has|have|had|is|are|was|were|won|wins|lost|loses|scored|score|born|died|invented|created|released|dropped|increased|decreased|rose|fell|plays|played)\b",
    re.IGNORECASE,
)


def _normalize_for_embedded_claim(sentence):
    """
    Removes common conversational lead-ins so embedded factual clauses are
    easier for the classifier to recognize.
    """
    if not sentence:
        return ""

    cleaned = re.sub(r"\s+", " ", sentence).strip()

    for pattern in _LEAD_IN_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def _looks_like_no_claim(sentence):
    if not sentence:
        return True

    stripped = sentence.strip().lower()
    if len(stripped) < 4:
        return True

    if stripped.startswith(_NON_VERIFIABLE_PREFIXES):
        return True

    has_question_mark = sentence.strip().endswith("?")
    starts_like_question = _QUESTION_PATTERN.match(stripped)

    if starts_like_question:
        return True

    if has_question_mark and not _FACTUAL_ASSERTION_PATTERN.search(stripped):
        return True

    for pattern in _SUBJECTIVE_VALUE_PATTERNS:
        if re.search(pattern, stripped, flags=re.IGNORECASE):
            return True

    return False


def _looks_like_no_context(sentence):
    stripped = sentence.strip().lower()
    return stripped.startswith(_NO_CONTEXT_PREFIXES)


def _normalize_model_label(text):
    if not text:
        return "NO"

    match = _LABEL_PATTERN.search(text)
    if not match:
        return "NO"

    return match.group(1).upper()


def analyze_verifiability(sentence):
    """
    Returns a structured classification result with a cleaned claim candidate.
    """
    normalized_sentence = _normalize_for_embedded_claim(sentence)
    candidate_sentence = normalized_sentence or sentence.strip()

    if _looks_like_no_claim(candidate_sentence):
        return {
            "label": "NO",
            "cleaned_claim": "",
            "original_sentence": sentence,
            "normalized_sentence": candidate_sentence,
        }

    if _looks_like_no_context(candidate_sentence):
        return {
            "label": "NO_CONTEXT",
            "cleaned_claim": "",
            "original_sentence": sentence,
            "normalized_sentence": candidate_sentence,
        }

    prompt = f"""
    You are a precision classification engine for a real-time fact-checking application.
    Your objective is to evaluate a spoken sentence and categorize it into EXACTLY one of THREE categories: YES, NO, or NO_CONTEXT.

    RULES:
    1. YES (Verifiable Claim): The sentence is a complete assertion that can be objectively proven TRUE or FALSE through evidence. It contains a clear subject and claims a specific fact, event, or status.
    - Important: If the sentence starts with an opinion/discourse lead-in (for example, "I think that...", "It's common sense that...", "Everyone knows that...") but contains a concrete factual proposition, classify as YES.
    - The claim can appear in the middle of a longer sentence, as long as there is a factual proposition that can be isolated.
    - Subjective value judgments without an explicit measurable standard (for example, "best player in the world", "good for the country", "better than Messi") are NOT verifiable and should be NO.
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
    Sentence: "It's common sense that the Earth is flat." -> YES
    Sentence: "I think that Paris is the capital of France." -> YES
    Sentence: "I feel this movie is boring." -> NO
    Sentence: "Cristiano Ronaldo is the best player in the world." -> NO
    Sentence: "Donald Trump is good for the country." -> NO
    Sentence: "Cristiano Ronaldo is better than Messi." -> NO

    ORIGINAL SENTENCE: "{sentence}"
    CANDIDATE CLAIM: "{candidate_sentence}"
    OUTPUT:
    """

    try:
        response = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0,
        )
        label = _normalize_model_label(response.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        label = "NO"

    cleaned_claim = candidate_sentence if label == "YES" else ""

    return {
        "label": label,
        "cleaned_claim": cleaned_claim,
        "original_sentence": sentence,
        "normalized_sentence": candidate_sentence,
    }

def check_if_verifiable(sentence):
    return analyze_verifiability(sentence)["label"]