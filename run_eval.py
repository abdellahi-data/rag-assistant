# tiny eval harness: run fixed questions through the pipeline, check each answer holds the expected fact.
# run: python -m eval

import sys
from rag import RagPipeline

# (question, expected substring in the answer). "__REFUSE__" means we expect an "i don't know".
CASES = [
    ("What was Voltaris revenue in FY2025?", "24.6"),
    ("How many employees work at Voltaris?", "38,400"),
    ("Where is Voltaris headquartered?", "Amsterdam"),
    ("In what year was Voltaris founded?", "2016"),
    ("What is the range of the Orion?", "780"),
    ("Who is the CFO of Voltaris?", "Lindqvist"),
    ("What is the name of the autonomous driving system?", "Halo"),
    ("What is the range of the Voltaris Falcon?", "__REFUSE__"),
]

REFUSAL_HINTS = ("don't know", "do not know", "couldn't find", "not mention", "no mention")


def looks_like_refusal(answer):
    a = answer.lower()
    return any(h in a for h in REFUSAL_HINTS)


def main():
    pipe = RagPipeline()
    passed = 0
    for question, expected in CASES:
        answer, _ = pipe.answer(question)
        if expected == "__REFUSE__":
            ok = looks_like_refusal(answer)
        else:
            ok = expected.lower() in answer.lower()
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {question}")
        if not ok:
            print(f"       expected: {expected!r}")
            print(f"       got:      {answer[:120]!r}")
    

    total = len(CASES)
    print(f"\n{passed}/{total} passed")

    # exit non-zero if anything failed, so the workflow CI marks the run red in github actions
    if passed < total:
        sys.exit(1)

if __name__ == "__main__":
    main()