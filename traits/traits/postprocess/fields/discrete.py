import pandas as pd

from .field import Field

class DiscreteField(Field):
        
    accdb_traits = None
    
    @classmethod
    def set_accdb_traits(cls, ents, accdb_terms):
        accdb_traits = set()
        trait_ents = [ent for ent in ents if ent.label_ == 'TRAIT']
        for ent in trait_ents:
            term = ent.text.lower().replace('-', '_')  
            part = ent.sent._.anatomical_part.lemma_ if ent.sent._.anatomical_part else None
            for row in accdb_terms[(accdb_terms.term == term) | (accdb_terms.term == ent.lemma_)].itertuples(): 
                accdb_traits.add((row.trait, row.character, part))
                
        cls.accdb_traits = pd.DataFrame(accdb_traits, columns=['trait', 'character', 'part'])    
                  
    def __init__(self, doc, name, part=None, require_part=True, accdb_name=None):
        super().__init__(doc, name, part, require_part) 
        self.accdb_name = accdb_name if accdb_name else self.name        
        self._value = self.get_accdb_chars()
        
    def get_accdb_chars(self):
        mask = self.accdb_traits['trait'] == self.accdb_name
                
        if self.part:
            mask = (mask) & (self.accdb_traits['part'].isin(self.part_synonyms))
                        
        accdb_chars = self.accdb_traits[mask] 
            
        return set(accdb_chars.character.values)