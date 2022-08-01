import itertools
from genpipes import compose, declare
from adept.config import RAW_DATA_DIR
import pandas as pd
from pathlib import Path
from collections.abc import Iterable

from adept.mongo import Mongo
from adept.config import logger
    
@declare.processor()
def mongo_processor(treatments, collection):
    mongo = Mongo()   
    mongo.drop_collection(collection)
    result = mongo.insert_many(collection, treatments)
    logger.info(f'Inserted {len(result.inserted_ids)} records into {collection}')
    return result.inserted_ids

@declare.generator() 
@declare.datasource(inputs=[RAW_DATA_DIR / 'peatland-species.csv'])
def species_datasource(path: Path):
    df = pd.read_csv(path)
    yield from df['Species name or special variable'].values

@declare.processor() 
def source_processor(taxa: Iterable = None, **kwargs):
    
    cls = kwargs.get('cls')
    limit = kwargs.get('limit')
    source = cls()
    counter = itertools.count()
    
    # Create an iterable source, depending on if the source 
    # Expacts a taxon parameter or not
    if taxa:
        iterable_source = map(source, taxa)
    else:
        iterable_source = source()
        
    for treatment in iterable_source:
        count = next(counter) 
        
        if count and count % 10 == 0:        
            logger.info(f'{count} records processed')               
        
        if limit and count >= limit:
            break  
        
        yield treatment.asdict() 