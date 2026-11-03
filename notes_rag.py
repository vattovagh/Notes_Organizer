"""
Question answering over your notes.

  python notes_rag.py ingest <folder>        OCR + chunk + embed notes into the vector store
  python notes_rag.py ask "question" [--subject Mathematics] [--k 4]
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="ingest a folder of note images / .txt files")
    p_ingest.add_argument("folder")
    p_ingest.add_argument("--max-words", type=int, default=200)
    p_ingest.add_argument("--overlap", type=int, default=40)

    p_ask = sub.add_parser("ask", help="ask a question about your notes")
    p_ask.add_argument("question")
    p_ask.add_argument("--subject", help="only search notes in this subject")
    p_ask.add_argument("--k", type=int, default=4)

    args = parser.parse_args()

    if args.command == "ingest":
        from rag.ingest import ingest_folder
        rows = ingest_folder(args.folder, args.max_words, args.overlap)
        print(f"Ingested {len(rows)} notes, {sum(r[2] for r in rows)} chunks.")
    else:
        from rag.qa import ask
        result = ask(args.question, k=args.k, subject=args.subject)
        print(result["answer"])
        print("\nSources:")
        for h in result["hits"]:
            print(f"  [{h['source']}] ({h['subject']}) distance={h['distance']:.3f}")


if __name__ == "__main__":
    main()
