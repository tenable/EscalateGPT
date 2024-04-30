from abc import ABC, abstractmethod


class AiClient(ABC):
    def __init__(self, apikey: str, model: str, temperature: float):
        self.temperature = temperature
        self.model = model
        self.apikey = apikey

    @abstractmethod
    def ask(self, user_prompt):
        pass
