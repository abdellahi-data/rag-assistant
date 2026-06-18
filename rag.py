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


# stitch the retrieved chunks and the question into one prompt
def build_prompt(question, hits):
    blocks = []
    for score, c in hits:
        blocks.append(f"[{c.source} p.{c.page}]\n{c.text}")
    context = "\n\n---\n\n".join(blocks)
    return f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"


class RagPipeline:
    def __init__(self, cfg: Config = config):
        self.cfg = cfg
        self.embedder = get_embedder(cfg)
        self.llm = get_llm(cfg)
        self.store = FaissVectorStore.load(cfg.index_dir)   # load the index built by ingest.py

    def answer(self, question):
        q_vec = self.embedder.embed_query(question)         # 1. question -> vector
        hits = self.store.search(q_vec, self.cfg.top_k)     # 2. find closest chunks
        prompt = build_prompt(question, hits)               # 3. build grounded prompt
        answer = self.llm.generate(prompt, system=SYSTEM_PROMPT)  # 4. ask the model
        sources = [c for _, c in hits]
        return answer, sources