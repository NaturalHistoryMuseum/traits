import typer
import pandas as pd
from pathlib import Path

from traits.preprocess import preprocessors


def preprocess(input_path: Path, output_path: Path):
    
    df = pd.read_csv(input_path)
    
    taxon_cols = {
        'group',
        'family',
        'taxon',
    }
    
    desc_cols = list(set(df.columns) - taxon_cols)
    
    def apply_preprocessors(text):

        if not pd.isnull(text):
            for preprocessoor in preprocessors:
                text = preprocessoor(text)
                
        return text
    
    df[desc_cols] = df[desc_cols].applymap(apply_preprocessors)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')    
    

if __name__ == "__main__":
    typer.run(preprocess)
