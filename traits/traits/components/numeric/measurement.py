from spacy.matcher import Matcher
from spacy.tokens import Span, Token
from spacy.util import filter_spans
from pint.errors import UndefinedUnitError

from adept.components.base import BaseComponent
from adept.config import unit_registry, logger

class NumericMeasurement(BaseComponent):
    
    """
    
    Match on QUANTITY and CARDINAL containing CM, MM, M, and set the measurement_unit
    

    Returns:
        doc: doc object with measurement_unit extension
    """
    
    # Has to come after dimensions, so any conjoined dimensions are split   
    pipeline_config = {'after': 'numeric_dimensions'}
       
    name = 'numeric_measurements'

    def __init__(self, nlp):                 

        super().__init__(nlp)
        self.nlp = nlp
        self.matcher = Matcher(nlp.vocab)          
        self.matcher.add('MEASUREMENT', [[{"ENT_TYPE": "QUANTITY", "OP": "+"}, {"LOWER": {"REGEX": r'^cm$|^mm$|^m$'}}]]) 
        self.matcher.add('MEASUREMENT', [[{"ENT_TYPE": "CARDINAL", "OP": "+"}, {"LOWER": {"REGEX": r'^cm$|^mm$|^m$'}}]])
        self.matcher.add('VOLUME', [[{"ENT_TYPE": "QUANTITY", "OP": "+"}, {"LOWER": {"REGEX": r'^mm³$|^cm³$'}}]]) 
        self.matcher.add('VOLUME', [[{"ENT_TYPE": "CARDINAL", "OP": "+"}, {"LOWER": {"REGEX": r'^mm³$|^cm³$'}}]])
         
        Span.set_extension("measurement_unit", default=None, force=True)
        Span.set_extension("measurements", default=[], force=True)
        Span.set_extension("volume_measurements", default=[], force=True)

    def __call__(self, doc):

        # Filter span, removes overlaps and preferring longest span         
        span_matches = filter_spans([
            Span(doc, start, end, self.nlp.vocab.strings[match_id]) for match_id, start, end in self.matcher(doc)
        ])
        
        for span in span_matches:
            # Unit will always be the last token as per the matcher pattern
            unit_token = span[-1]
            try:           
                unit = getattr(unit_registry, unit_token.lemma_)
            except UndefinedUnitError:
                logger.error(f'Unit {unit_token.lemma_} is not defined in pint')
            else:
                span._.measurement_unit = unit    
                if span.label_ == 'MEASUREMENT':
                    span.sent._.measurements.append(span)
                elif span.label_ == 'VOLUME':
                    span.sent._.volume_measurements.append(span)

        return doc 
    
import spacy    
    
    
if __name__ == '__main__':
    
    nlp = spacy.load("en_core_web_trf")

    ner = NumericMeasurement(nlp)

    text = 'Seed ovoid to ellipsoid, 1.5-2 x 1.7-2.2 cm, apex impressed 3mm³ and long.' 

    doc = nlp(text)
    ner(doc)

