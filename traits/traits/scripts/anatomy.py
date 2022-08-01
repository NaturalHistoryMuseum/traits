
import yaml
import typer
from pathlib import Path

from adept.utils.patterns import Patterns

 
    
def read_anatomical_parts(input_path):
    f = yaml.full_load(input_path.open())
    for term, synonym in f.items():
        yield term
        if synonym:
            yield from synonym 
        else:
            yield f'{term}s'


def main(input_path: Path, output_path: Path):
    
    patterns = Patterns()
    
    for part in read_anatomical_parts(input_path):
        patterns.add(part, 'PART')
    
    patterns.to_jsonl(output_path)
    
    

if __name__ == "__main__":
    typer.run(main)