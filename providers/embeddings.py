# turns text into vectors. same idea as llm.py: one interface, ollama local / bedrock cloud, picked by config.
import json
from abc import ABC, abstractmethod

import requests

from src.config import Config


# the contract: anything that can turn texts into embedding vectors
class EmbeddingClient(ABC):
    @abstractmethod
    def embed(self, texts):
        ...

    # embedding a single query is just the batch path with one item
    def embed_query(self, text):
        return self.embed([text])[0]


# local embeddings via ollama, used while developing
class OllamaEmbedder(EmbeddingClient):
    def __init__(self, cfg: Config):
        self.host = cfg.ollama_host
        self.model = cfg.ollama_embed_model

    def embed(self, texts):
        # ollama embeds one text per call, so loop over them
        out = []
        for t in texts:
            r = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": t},
                timeout=120,
            )
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return out


# same thing through bedrock (titan), used once deployed
class BedrockEmbedder(EmbeddingClient):
    def __init__(self, cfg: Config):
        import boto3  # only needed in the cloud

        self.client = boto3.client("bedrock-runtime", region_name=cfg.aws_region)
        self.model = cfg.bedrock_embed_model

    def embed(self, texts):
        out = []
        for t in texts:
            r = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps({"inputText": t}),
            )
            out.append(json.loads(r["body"].read())["embedding"])
        return out


# factory: config decides which backend the rest of the app gets
def get_embedder(cfg: Config) -> EmbeddingClient:
    if cfg.embedding_provider == "local":
        return OllamaEmbedder(cfg)
    if cfg.embedding_provider == "bedrock":
        return BedrockEmbedder(cfg)
    raise ValueError(f"bad EMBEDDING_PROVIDER: {cfg.embedding_provider}")