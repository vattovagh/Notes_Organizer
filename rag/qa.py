"""Answer questions about the notes using retrieved chunks and Claude."""

from typing import Dict, List, Optional

from rag.store import search

MODEL = "claude-sonnet-5-5"

SYSTEM_PROMPT = (
    "You answer questions about the user's personal notes. Use ONLY the note excerpts "
    "provided. Cite the source of each claim in square brackets, like [calculus_week3]. "
    "The excerpts come from OCR and may contain errors; read through them sensibly. "
    "If the excerpts do not contain the answer, say \"I couldn't find that in your notes.\" "
    "and do not guess."
)


def build_context(hits: List[Dict]) -> str:
    return "\n\n".join(f"[{h['source']}] ({h['subject']})\n{h['text']}" for h in hits)


def ask(question: str, k: int = 4, subject: Optional[str] = None, client=None) -> Dict:
    """Retrieve top-k chunks and generate a grounded answer. Returns {answer, hits}."""
    hits = search(question, k=k, subject=subject)
    if not hits:
        return {"answer": "No notes have been ingested yet.", "hits": []}

    if client is None:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Note excerpts:\n\n{build_context(hits)}\n\nQuestion: {question}",
        }],
    )
    return {"answer": message.content[0].text, "hits": hits}
