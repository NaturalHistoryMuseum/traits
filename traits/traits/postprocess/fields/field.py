from pathlib import Path
import yaml

from adept.config import ASSETS_DIR, spacy_config


class Field():  
    
    anatomical_parts_path = Path(ASSETS_DIR / spacy_config['file']['anatomical_parts'])
    anatomical_parts = yaml.full_load(anatomical_parts_path.open())
    anatomical_parts_synonyms = [syns + [part] for part, syns in anatomical_parts.items() if syns]
    
    def __init__(self, doc, name, part, require_part):
        self.name = name
        self.part = part
        self.require_part = require_part
        self.part_synonyms = self._get_part_synonyms(part) or []
        self._value = None

    @property
    def value(self):
        return self._value
    
    def as_string(self):
        if isinstance(self.value, (list, set)):
            return ','.join(set(self.value))
                    
        return self.value
    
    def _get_part_synonyms(self, part):
        for syns in self.anatomical_parts_synonyms:
            if part in syns:
                return syns
            
    def get_sents_filtered_by_part(self, doc):
        if not self.require_part:
            yield from doc.sents
        
        for sent in doc.sents:
            if self.sent_matches_part(sent):
                yield sent
                           
    def sent_matches_part(self, sent):
        if not self.part:
            return True
        else:
            sent_part = self._get_sent_part(sent)
            if sent_part == self.part or sent_part in self.part_synonyms:
                return True
            
        return False
    
    def _get_sent_part(self, sent):
        if sent.start == 0:
            return 'plant'
        elif sent._.anatomical_part:
            return sent._.anatomical_part.lemma_   