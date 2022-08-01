import yaml
import itertools

from adept.config import PROCESSED_DATA_DIR

class PlantPartOntology():
    
    def __init__(self):
        self._terms = self._load_terms()

    @property
    def terms(self):
        # Unpack keys
        return [*self._terms]

    @property
    def plural(self):
        return list(itertools.chain(*self._terms.values()))
            
    @property
    def combined(self):    
        return sorted(self.terms + self.plural)
            
    @staticmethod
    def _load_terms():
        
        ontology_file = PROCESSED_DATA_DIR / 'ontology' / 'structural-parts.yaml'  
                
        return {
            # If plural form isn't specified, pluralised version is just with an s
            term: plural_form if plural_form else [f'{term}s'] for 
            term, plural_form in yaml.full_load(ontology_file.open()).items()
        }
        
    


                
