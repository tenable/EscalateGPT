from abc import ABC, abstractmethod

from const.my_logger import MyLogger


class Cloud(ABC):
    def __init__(self):
        self.logger = MyLogger(__name__)
        pass

    @abstractmethod
    def _connect(self, **kwargs):
        pass

    @abstractmethod
    def start(self) -> str:
        pass
