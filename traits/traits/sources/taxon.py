from __future__ import annotations
import pandas as pd
from genpipes import compose, declare
from pathlib import Path
from collections.abc import Iterable
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from abc import ABCMeta, abstractmethod, ABC
from enum import Enum
from collections import OrderedDict
from urllib import parse
from adept.config import logger
from dataclasses import dataclass, field
from typing import List



@dataclass
class TaxonDescription:
    source: str
    text: str 
    
    def asdict(self):
        return self.__dict__

@dataclass
class TaxonProperties:
    source: str
    props: dict 
    
    def asdict(self):
        return self.__dict__
    
@dataclass
class TaxonTreatment(ABC):
    
    name: str
    _id: str = None
    parent: str = None
    # FIXME. Why are these lists?? We do not have one to many. Source is on description???
    # FIXME: So why even have these???
    _descriptions: List[TaxonDescription] = field(init=False, default_factory=list)
    _properties: List[TaxonProperties] = field(init=False, default_factory=list)
  
    @property    
    def descriptions(self):
        return self._descriptions
    
    def id(self):
        return self._id
  
    def add_description(self, description:TaxonDescription):
        self._descriptions.append(description)

    def set_parent(self, taxon: str):
        self.parent = taxon

    def asdict(self):
        
        # TODO: This could be tidied up a bit
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v}

        if self.descriptions:
            d['descriptions'] = [d.asdict() for d in self.descriptions]
 
        return d
    
    def __repr__(self):
        return f'TaxonTreatment({self.name})'