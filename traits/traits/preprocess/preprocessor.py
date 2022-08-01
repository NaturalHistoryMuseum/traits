from abc import ABC, abstractmethod


class Preprocessor(ABC):
    
    @property
    @abstractmethod
    def preprocess(self, text):
        return text   

    def __call__(self, text):
        return self.preprocess(text)