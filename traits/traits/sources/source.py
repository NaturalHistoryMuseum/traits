import tldextract
from abc import ABCMeta, abstractmethod, ABC
from enum import Enum
import inspect

class Source(ABC):
    
    class Type(Enum):
        DESCRIPTIONS = 1
        PROPERTIES = 2       
    
    @property
    @abstractmethod
    def base_url(self):
        pass
    
    @property
    @abstractmethod
    def source_type(self):
        pass    
    
    @classmethod
    @property
    def name(cls):
        return tldextract.extract(cls.base_url).domain

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            if not inspect.isabstract(subclass):
                yield subclass

    @abstractmethod
    def __call__(self):
        pass    
    
class DescriptionsSource(Source):
    
    source_type = Source.Type.DESCRIPTIONS
    
    
class PropertiesSource(Source):
    
    source_type = Source.Type.PROPERTIES    
    
    
class SourceFactory(object):
    
    def factory(source_name, source_type):
        for cls in Source.get_subclasses():
            if cls.name == source_name and cls.source_type.name.lower() == source_type:
                return cls

    factory = staticmethod(factory)     