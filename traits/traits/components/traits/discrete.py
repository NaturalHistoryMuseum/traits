import csv

import spacy
from spacy.language import Language
from spacy.tokens import Doc
from spacy.matcher import Matcher
from spacy.tokens import Span, Token
from spacy import displacy
from spacy.pipeline import EntityRuler
from pathlib import Path

from traits.components.base import BaseComponent
from traits.config import CORPUS_DIR, spacy_config


class DiscreteTraitsEntity(EntityRuler, BaseComponent):
    
    name = 'discrete_traits_entity'
    
    pipeline_config = {'after': 'anatomical_entity'}    
    
    patterns_file = Path(CORPUS_DIR / spacy_config['file']['trait_patterns'])

    def __init__(self, nlp, *args, **cfg):
        super().__init__(nlp, overwrite_ents=True, *args, **cfg)
        
        self.from_disk(self.patterns_file)

                


if __name__ == '__main__':

    nlp = spacy.load("en_core_web_trf")

    ner = DiscreteTraitsEntity(nlp)

    text = 'Herbs, perennial, 40-100 cm tall, with long rhizomes; stems erect, unbranched or branched in upper part, often with short sterile branches at leaf axils above middle, striate, usually white villous.' 
    
    
    
    doc = nlp(text)

    doc = ner(doc)
    for ent in doc.ents:
        print(ent.label_, ent.text)