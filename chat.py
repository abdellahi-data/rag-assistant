# terminal chat loop: ask questions about the pdfs, print answers with sources. run: python -m chat
from src.config import config
from rag import RagPipeline


def main():
    print(f"loading index ({config.llm_provider} llm, {config.embedding_provider} embeddings) ...")
    pipe = RagPipeline(config)
    print("ready. ask a question (ctrl-c to quit).\n")
    try:
        while True:
            q = input("you > ").strip()
            if not q:
                continue                       # ignore empty input
            answer, sources = pipe.answer(q)
            print(f"\nbot > {answer}\n")
            # show unique source citations, sorted
            cites = sorted({f"{s.source} p.{s.page}" for s in sources})
            print("      sources: " + ", ".join(cites) + "\n")
    except (KeyboardInterrupt, EOFError):
        print("\nbye.")


if __name__ == "__main__":
    main()