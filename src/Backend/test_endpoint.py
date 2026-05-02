#!/usr/bin/env python3
"""
Test the /transcript/analyze endpoint via HTTP.
Requires the FastAPI backend to be running on http://localhost:8000

Run this after starting the backend:
  python test_endpoint.py
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"
ANALYZE_ENDPOINT = f"{BACKEND_URL}/transcript/analyze"

SAMPLE_TRANSCRIPT = """
The Earth orbits around the Sun. This is a fundamental fact of astronomy.
I think pizza is the best food in the world.
Portugal won the UEFA Euro 2016 tournament.
Tomorrow it will probably rain in Lisbon.
The moon is made of rock and dust, similar in composition to Earth.
He discovered something interesting.
Water boils at 100 degrees Celsius at sea level.
I believe that AI will change everything.
"""

def main():
    print("=" * 70)
    print("TESTING /transcript/analyze ENDPOINT")
    print("=" * 70)
    print()
    
    payload = {"transcript": SAMPLE_TRANSCRIPT}
    
    print(f"Sending POST to: {ANALYZE_ENDPOINT}")
    print(f"Payload: {json.dumps(payload, indent=2)[:100]}...")
    print()
    
    try:
        response = requests.post(ANALYZE_ENDPOINT, json=payload)
        response.raise_for_status()
        
        results = response.json()
        
        print("=" * 70)
        print(f"STATUS: {response.status_code}")
        print("=" * 70)
        print()
        
        print("Response Summary:")
        print(f"  Total items: {len(results)}")
        
        results_count = sum(1 for r in results if r['type'] == 'results')
        resume_count = sum(1 for r in results if r['type'] == 'resume')
        
        print(f"  Verifiable claims: {results_count}")
        print(f"  Overall summaries: {resume_count}")
        print()
        
        print("=" * 70)
        print("FULL RESPONSE")
        print("=" * 70)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend at", BACKEND_URL)
        print("Make sure the FastAPI backend is running:")
        print("  cd src/Backend && uvicorn app:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
