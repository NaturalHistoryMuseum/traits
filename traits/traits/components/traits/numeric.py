from spacy.language import Language
from spacy.tokens import Doc
from spacy.matcher import Matcher
from spacy.tokens import Span, Token
from spacy import displacy
from spacy.util import filter_spans

from traits.components.base import BaseComponent

class NumericTraitsEntity(BaseComponent):
    
    name = 'numeric_trait_entity'
    
    def __init__(self, nlp):                 

        super().__init__(nlp)
        self.matcher = Matcher(nlp.vocab)  
        
        # FIXME: This should come straight from fields 
        
        self.matcher.add(
            'STAMEN NUMBER', 
            [[{"POS": "NUM"}, {"LEMMA": "stamen"}]]
        )
        self.matcher.add(
            'STAMENOID NUMBER', 
            [[{"POS": "NUM"}, {"LEMMA": "stamenoid"}]]
        )        
        for term in ['carpel', 'ovary', 'ovum', 'ovaries']:        
            self.matcher.add(
                'CARPEL/OVARY NUMBER', 
                [[{"POS": "NUM"}, {"LEMMA": term}]]
            )   
                       
        Span.set_extension("trait_value", default=None, force=True) 
    
    def __call__(self, doc):
        
        ents = list(doc.ents)
        for match_id, start, end in self.matcher(doc):
            string_id = self.matcher.vocab.strings[match_id]
            entity = Span(doc, start, end, label=string_id)
            
            try:
                num = [int(token.text) for token in entity if token.pos_ == 'NUM'][0]
            except ValueError:
                continue
            
            entity._.set("trait_value", num)             
            ents.append(entity)
            
        doc.ents = filter_spans(ents)
            
        return doc
      