import tldextract
from abc import ABCMeta, abstractmethod, ABC

class DescriptionSource(metaclass=ABCMeta):
    @abstractmethod
    def get_taxon_description(self, taxon_name):
        pass
    
    @property
    @abstractmethod
    def base_url(self):
        pass  
    
    @classmethod
    @property
    def name(cls):
        return tldextract.extract(cls.base_url).domain    