from dataclasses import dataclass


@dataclass
class RetrievedMemory:

    source: str

    content: str

    score: float

    metadata: dict | None = None