#!/usr/bin/env python3
"""
Simple test script for the transcript analysis function.
Run from the Backend folder: python test_transcript_analyze.py
"""

import json
from fact_checker import analyze_transcript

# Sample transcript with a mix of verifiable and non-verifiable content
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
    print("TRANSCRIPT ANALYSIS TEST")
    print("=" * 70)
    print()
    
    print("Input Transcript:")
    print("-" * 70)
    print(SAMPLE_TRANSCRIPT.strip())
    print()
    print("-" * 70)
    print()
    
    print("Analyzing transcript...")
    print()
    
    try:
        results = analyze_transcript(SAMPLE_TRANSCRIPT)
        
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()
        
        for i, item in enumerate(results, 1):
            print(f"[{i}] Type: {item['type'].upper()}")
            print(f"    Text: {item['text']}")
            
            if item['type'] == 'results':
                print(f"    Confidence: {item['confidence']}%")
                print(f"    Explanation: {item['explanation']}")
                if item['sources']:
                    print(f"    Sources: {len(item['sources'])} found")
                    for source in item['sources'][:2]:  # Show first 2 sources
                        print(f"      - {source[:80]}...")
            
            print()
        
        # Pretty print the full JSON
        print("=" * 70)
        print("FULL JSON OUTPUT")
        print("=" * 70)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
