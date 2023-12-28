from abc import ABC, abstractmethod

from static.my_logger import MyLogger


class Cloud(ABC):
    def __init__(self):
        self.logger = MyLogger(__name__)
        pass

    def _connect(self):
        pass

    @abstractmethod
    def start(self):
        pass
