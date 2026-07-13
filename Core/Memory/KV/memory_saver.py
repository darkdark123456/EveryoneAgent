from typing import Optional
from langgraph.checkpoint.memory import InMemorySaver

class MemorySaver:
    _instance: Optional["MemorySaver"] = None
    _memorysaver: InMemorySaver

    def __new__(cls, *args, **kwargs) -> "MemorySaver":
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_memorysaver"):
            return
        self._memorysaver = InMemorySaver()

    def get_memorysaver(self) -> InMemorySaver:
        return self._memorysaver

