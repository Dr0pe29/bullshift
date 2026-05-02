#!/usr/bin/env python3
"""
Simple evaluation script for check_verifiable.py.

Usage:
  python eval_verifiable.py
  python eval_verifiable.py --dataset verifiable_eval.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from check_verifiable import analyze_verifiability

DEFAULT_DATASET = Path(__file__).with_name("verifiable_eval.json")
LABELS = ("YES", "NO", "NO_CONTEXT")


def load_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON array of {text, label} objects")

    return data


def safe_div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate verifiability classification quality.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="Path to JSON dataset file")
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)

    totals = Counter()
    correct = Counter()
    confusion = defaultdict(Counter)
    failures = []

    for item in dataset:
        text = item["text"]
        expected = item["label"].upper()
        result = analyze_verifiability(text)
        predicted = result["label"].upper()
        cleaned = result.get("cleaned_claim", "")

        totals[expected] += 1
        confusion[expected][predicted] += 1

        if predicted == expected:
            correct[expected] += 1
        else:
            failures.append({
                "text": text,
                "expected": expected,
                "predicted": predicted,
                "cleaned_claim": cleaned,
            })

    total_items = sum(totals.values())
    total_correct = sum(correct.values())
    accuracy = safe_div(total_correct, total_items)

    print("=" * 72)
    print("VERIFIABILITY EVAL")
    print("=" * 72)
    print(f"Dataset: {args.dataset}")
    print(f"Samples: {total_items}")
    print(f"Accuracy: {accuracy:.1%}")
    print()

    print("Per-label results:")
    for label in LABELS:
        label_total = totals[label]
        label_correct = correct[label]
        precision_like = safe_div(label_correct, sum(confusion[x][label] for x in LABELS))
        recall = safe_div(label_correct, label_total)
        print(
            f"  {label:<10} total={label_total:<3} correct={label_correct:<3} "
            f"precision={precision_like:.1%} recall={recall:.1%}"
        )

    print()
    print("Confusion matrix (expected -> predicted):")
    header = " " * 12 + " ".join(f"{label:>11}" for label in LABELS)
    print(header)
    for expected in LABELS:
        row = f"{expected:>11} "
        for predicted in LABELS:
            row += f"{confusion[expected][predicted]:>11} "
        print(row)

    if failures:
        print()
        print("Misclassifications:")
        for failure in failures:
            print(
                f"- expected={failure['expected']:<10} predicted={failure['predicted']:<10} "
                f"text={failure['text']}"
            )
            if failure["cleaned_claim"]:
                print(f"  cleaned_claim={failure['cleaned_claim']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
