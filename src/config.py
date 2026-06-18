# app settings, read from env vars (or defaults). flips between local and bedrock.
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def env(name, default):
    return os.environ.get(name, default)


@dataclass
class Config:
    # local or bedrock
    llm_provider: str = field(default_factory=lambda: env("LLM_PROVIDER", "local"))
    embedding_provider: str = field(default_factory=lambda: env("EMBEDDING_PROVIDER", "local"))

    ollama_host: str = field(default_factory=lambda: env("OLLAMA_HOST", "http://localhost:11434"))
    ollama_llm_model: str = field(default_factory=lambda: env("OLLAMA_LLM_MODEL", "llama3.2"))
    ollama_embed_model: str = field(default_factory=lambda: env("OLLAMA_EMBED_MODEL", "nomic-embed-text"))

    aws_region: str = field(default_factory=lambda: env("AWS_REGION", "us-east-1"))
    bedrock_llm_model: str = field(default_factory=lambda: env("BEDROCK_LLM_MODEL", "anthropic.claude-haiku-4-5-20251001-v1:0"))
    bedrock_embed_model: str = field(default_factory=lambda: env("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0"))

    chunk_size: int = field(default_factory=lambda: int(env("CHUNK_SIZE", "800")))
    chunk_overlap: int = field(default_factory=lambda: int(env("CHUNK_OVERLAP", "150")))
    top_k: int = field(default_factory=lambda: int(env("TOP_K", "4")))

    pdf_dir: str = field(default_factory=lambda: env("PDF_DIR", "data/pdfs"))
    index_dir: str = field(default_factory=lambda: env("INDEX_DIR", "data/index"))


config = Config()