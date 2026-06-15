# talks to the model. one interface, two backends (ollama local / bedrock cloud), picked by config.
from abc import ABC, abstractmethod

import requests

from src.config import Config


# the contract: anything that can turn a prompt into text
class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt, system=None): ...


# local model served by ollama, used while developing
class OllamaLLM(LLMClient):
    def __init__(self, cfg: Config):
        self.host = cfg.ollama_host
        self.model = cfg.ollama_llm_model

    def generate(self, prompt, system=None):
        # build the chat messages, system prompt first if we have one
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        # call ollama's local http api
        r = requests.post(
            f"{self.host}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()


# same thing but through bedrock, used once deployed
class BedrockLLM(LLMClient):
    def __init__(self, cfg: Config):
        import boto3  # only needed in the cloud, so import it here

        self.client = boto3.client("bedrock-runtime", region_name=cfg.aws_region)
        self.model = cfg.bedrock_llm_model

    def generate(self, prompt, system=None):
        # converse is the same shape for every bedrock model, so swapping models is just a config change
        kwargs = {
            "modelId": self.model,
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": 1024, "temperature": 0.2},
        }
        if system:
            kwargs["system"] = [{"text": system}]
        r = self.client.converse(**kwargs)
        return r["output"]["message"]["content"][0]["text"].strip()


# factory: config decides which backend the rest of the app gets
def get_llm(cfg: Config) -> LLMClient:
    if cfg.llm_provider == "local":
        return OllamaLLM(cfg)
    if cfg.llm_provider == "bedrock":
        return BedrockLLM(cfg)
    raise ValueError(f"bad LLM_PROVIDER: {cfg.llm_provider}")
