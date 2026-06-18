# the rag flow: embed the question, find relevant chunks, build a grounded prompt, ask the model.
from src.config import Config, config
from providers.embeddings import get_embedder
from providers.llm import get_llm
from vectorstore import Chunk, FaissVectorStore

# tells the model to answer only from the chunks we give it, and to cite them
SYSTEM_PROMPT = (
    "You answer questions about a company using ONLY the provided context. "
    "If the answer is not in the context, say you don't know. "
    "Cite the source document and page for each fact you use."
)

# below this similarity score a chunk is treated as irrelevant.
# this is embedding-model-specific. set to 0.1 FOR Titan's score range.
MIN_SCORE = 0.1

# if the model's answer starts with one of these, treat it as a refusal and hide sources
REFUSAL_MARKERS = ("i don't know", "i do not know", "don't know")


# stitch the retrieved chunks and the question into one prompt
def build_prompt(question, hits):
    blocks = []
    for score, c in hits:
        blocks.append(f"[{c.source} p.{c.page}]\n{c.text}")
    context = "\n\n---\n\n".join(blocks)
    return f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"


def is_refusal(answer):
    a = answer.strip().lower()
    return any(a.startswith(m) for m in REFUSAL_MARKERS)


class RagPipeline:
    def __init__(self, cfg: Config = config):
        self.cfg = cfg
        self.embedder = get_embedder(cfg)
        self.llm = get_llm(cfg)
        self.store = FaissVectorStore.load(cfg.index_dir)

    def answer(self, question):
        q_vec = self.embedder.embed_query(question)
        hits = self.store.search(q_vec, self.cfg.top_k)

        # drop clearly irrelevant chunks
        hits = [(s, c) for s, c in hits if s >= MIN_SCORE]

        # nothing relevant -> don't call the model, don't show sources
        if not hits:
            return "I don't know — I couldn't find anything relevant in the documents.", []

        prompt = build_prompt(question, hits)
        answer = self.llm.generate(prompt, system=SYSTEM_PROMPT)

        # if the model couldn't answer from the chunks, don't show misleading sources
        if is_refusal(answer):
            return answer, []

        sources = [c for _, c in hits]
        return answer, sources
    