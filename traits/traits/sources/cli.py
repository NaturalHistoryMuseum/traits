import click
import itertools
import inspect
from genpipes import compose, declare

from adept.sources import *
from adept.sources.source import Source, SourceFactory
from adept.sources.wikipedia import descriptions
from adept.sources.pipeline import mongo_processor, source_processor, species_datasource
from adept.config import logger

# FIXME: Error if source type props selected for efloares eg
@click.command()
@click.option('-s', '--source_name', type=click.Choice({cls.name for cls in Source.get_subclasses()}, case_sensitive=False), required=True)
@click.option('-t', '--source_type', type=click.Choice({cls.source_type.name.lower() for cls in Source.get_subclasses()}, case_sensitive=False), required=True)
@click.option('-l', '--limit', type=click.INT, default=None)
def main(source_name, source_type, limit):
            
    cls = SourceFactory.factory(source_name, source_type)
    collection = f'{source_name}.{source_type}'
    
    steps = [            
       ("Fetching data source", source_processor, {'cls':cls, 'limit': limit}),
       ("Inserting into mongo", mongo_processor, {'collection': collection})         
    ]

    # TODO Inspect cls __call__ for taxon parameter
    if source_name == 'wikipedia':
        steps.insert(0, ("Peatland species CSV", species_datasource, {}),)
        
    pipe = compose.Pipeline(steps=steps)

    output = pipe.run() 
    
    



if __name__ == '__main__':
    main()
    # print(list(Source.get_subclasses()))
    
