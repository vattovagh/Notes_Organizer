"""
Evaluate retrieval and answer quality against eval/questions.json.

Each question: {"question": str, "sources": [note stems that contain the answer],
                "answerable": bool, "reference": short expected answer (answerable only)}

Usage: python -m eval.run_eval [--k 4] [--no-judge]
"""

import argparse
import json
import os

from rag.metrics import first_relevant_rank, retrieval_scores
from rag.qa import MODEL, ask

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "questions.json")

JUDGE_PROMPT = """You are grading an answer from a notes question-answering system.

Question: {question}
Reference answer: {reference}
System answer: {answer}

Reply with JSON only: {{"correct": true/false, "reason": "<one sentence>"}}
"correct" is true if the system answer agrees with the reference answer."""

REFUSAL_PROMPT = """A notes question-answering system was asked a question that its notes do NOT answer.

Question: {question}
System answer: {answer}

Reply with JSON only: {{"refused": true/false}}
"refused" is true if the system said it couldn't find the answer instead of inventing one."""


def _judge(client, prompt: str) -> dict:
    message = client.messages.create(
        model=MODEL, max_tokens=200, messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip()
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=4, help="chunks retrieved per question")
    parser.add_argument("--no-judge", action="store_true", help="retrieval metrics only (no LLM calls)")
    args = parser.parse_args()

    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    client = None
    if not args.no_judge:
        import anthropic
        client = anthropic.Anthropic()

    ranks, correct, refused = [], [], []
    for q in questions:
        if args.no_judge:
            from rag.store import search
            hits = search(q["question"], k=args.k)
            answer = None
        else:
            result = ask(q["question"], k=args.k, client=client)
            hits, answer = result["hits"], result["answer"]

        if q["answerable"]:
            rank = first_relevant_rank([h["source"] for h in hits], q["sources"])
            ranks.append(rank)
            line = f"rank={rank or 'miss'}"
            if answer is not None:
                verdict = _judge(client, JUDGE_PROMPT.format(
                    question=q["question"], reference=q["reference"], answer=answer))
                correct.append(bool(verdict["correct"]))
                line += f" correct={verdict['correct']}"
        else:
            line = "unanswerable"
            if answer is not None:
                verdict = _judge(client, REFUSAL_PROMPT.format(question=q["question"], answer=answer))
                refused.append(bool(verdict["refused"]))
                line += f" refused={verdict['refused']}"
        print(f"- {q['question'][:70]:<70} {line}")

    print("\nRESULTS")
    for name, value in retrieval_scores(ranks, args.k).items():
        print(f"  {name}: {value:.2f}")
    if correct:
        print(f"  answer correctness: {sum(correct) / len(correct):.2f} ({len(correct)} questions)")
    if refused:
        print(f"  correct refusals:   {sum(refused) / len(refused):.2f} ({len(refused)} questions)")


if __name__ == "__main__":
    main()
