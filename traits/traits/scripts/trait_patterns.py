import click
import jsonlines
import typer
from pathlib import Path

from adept.traits.accdb import ACCDBTraits
from adept.utils.patterns import Patterns

 
def main(output_path: Path):
    
    accdb = ACCDBTraits()
    patterns = Patterns()
    
    colours = accdb.get_colours()
    terms = set(accdb.get_unique_terms()) - colours
    
    for term in terms:
        patterns.add(term, 'TRAIT')
    
    for colour in colours:
        patterns.add(colour, 'COLOUR')    
    
    patterns.to_jsonl(output_path)    
    



if __name__ == "__main__":
    typer.run(main)