# Testing the Transcript Analysis Function

Two simple ways to test the new transcript analyzer:

## Option 1: Direct Function Test (No Backend Required)

Fastest way to test the analysis logic directly:

```bash
cd src/Backend
python test_transcript_analyze.py
```

This runs the `analyze_transcript()` function with a sample transcript and prints:
- Each verifiable claim with confidence score, explanation, and sources
- The overall summary/review of the entire transcript
- Full JSON output

**Good for**: Quick local testing, debugging, understanding the output format

---

## Option 2: HTTP Endpoint Test (With Backend Running)

Test the actual `/transcript/analyze` endpoint:

**Terminal 1 - Start the backend:**
```bash
cd src/Backend
uvicorn app:app --reload
```

**Terminal 2 - Run the endpoint test:**
```bash
cd src/Backend
python test_endpoint.py
```

This sends a POST request to `http://localhost:8000/transcript/analyze` and displays the response.

**Good for**: Testing the full API integration, verifying the endpoint works

---

## Curl Alternative

If you prefer curl instead of Python:

```bash
curl -X POST http://localhost:8000/transcript/analyze \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Portugal won the UEFA Euro 2016. The Earth orbits the Sun. I think pizza is great."}'
```

---

## Expected Output Format

```json
[
  {
    "type": "results",
    "text": "Portugal won the UEFA Euro 2016 tournament",
    "confidence": 92,
    "explanation": "Portugal defeated France in the final...",
    "sources": ["Wikipedia - Portugal at UEFA Euro 2016", "..."]
  },
  {
    "type": "resume",
    "text": "Overall review of the entire transcript..."
  }
]
```

- **results**: Verifiable claims with confidence score and sources
- **resume**: Single overall summary at the end
