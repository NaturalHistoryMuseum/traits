import typer
import pandas as pd
import spacy
from pathlib import Path
from spacy.matcher import Matcher
from spacy.tokens import Span, Token
from adept.config import unit_registry
from spacy.util import filter_spans
from spacy.tokens import DocBin
from spacy import displacy
from sklearn.model_selection import train_test_split

from adept.components.registry import ComponentsRegistry
from adept.utils.expand import ExpandSpan

from adept.components.sentencizer import Sentencizer
from adept.components.ner.numeric.expand import NumericExpandNER
from adept.scripts.helpers import get_descriptions
from adept.config import LOG_DIR, logger

def main(input_path: Path, train_output_path: Path, test_output_path: Path, limit: int = 5):
        
    docs = []
    
    HTML_LOG_DIR = LOG_DIR / 'html'
    HTML_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Delete everything in the html log directory
    [f.unlink() for f in HTML_LOG_DIR.glob("*") if f.is_file()]
    
    nlp = spacy.load("en_core_web_trf")
    registry = ComponentsRegistry(nlp)
    registry.add_components([
        Sentencizer,
        NumericExpandNER
    ])
    
    taxa = set()       
    
    for taxon, description in get_descriptions(input_path):
        
        if taxon not in taxa:
            logger.info('Processing %s', taxon)  
            taxa.add(taxon)
        
        if limit and len(taxa) > limit:
            break
        
        doc = registry.nlp(description)
        
        sents = [sent for sent in doc.sents if sent._.is_expanded_numeric and sent_has_numeric_ent_types(sent) and sent_has_complex_numeric(sent) and not sent_is_2n(sent)]
         
        # Add all the sentences we want to train against to the docbin
        for sent in sents:
            docs.append(sent.as_doc())
             
        displacy.render(sents, style='ent', jupyter=True)                
        html = displacy.render(sents, style='ent', page=True, jupyter=False)   
        log_file = HTML_LOG_DIR / f'{taxon}.html'   
        
        with log_file.open("a") as f:
            f.write(description)
            f.write('----')
            f.write(html)  

    docs_train, docs_test = train_test_split(docs,test_size=0.2)
    DocBin(docs=docs_train).to_disk(train_output_path) 
    DocBin(docs=docs_test).to_disk(test_output_path) 

    logger.info('Writing %s training data sentences to %s & %s test to %s', len(docs_train), train_output_path, len(docs_test), test_output_path)    
    
def sent_has_complex_numeric(sent):

    MIN_NUMBER_LENGTH = 1
    
    # We don't want to add a load of training data with cardinals of length 1
    # So get the maximum length of numeric chars, and skip if not > 1         
    max_num_len = max([sum([len(t) for t in ent if t.pos_ == 'NUM']) for ent in sent.ents])

    return max_num_len > MIN_NUMBER_LENGTH      

def sent_has_numeric_ent_types(sent):
    ent_types = ['QUANTITY', 'CARDINAL']
    return any([e.label_ in ent_types for e in sent.ents])

def sent_is_2n(sent):
    return '2n' in [s.text for s in sent]

if __name__ == "__main__":
    typer.run(main)
