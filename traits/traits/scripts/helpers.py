import pandas as pd
import spacy
from pathlib import Path
from collections import namedtuple


def get_description_columns(df):
    taxon_cols = {
        'group',
        'family',
        'taxon',
        'genus'
    }

    # Add a sort so the columns are always the same order
    return sorted(list(set([c.lower() for c in df.columns]) - taxon_cols)) 

Description = namedtuple('Description', ['taxon', 'taxon_group', 'text', 'source']) 

def get_descriptions(input_path: Path):  
    
    df = pd.read_csv(input_path)
    
    # Treat lichens as Bryophytes
    df.loc[df.group == 'Lichen', 'group'] = 'Bryophyte'

    desc_cols = get_description_columns(df)

    for row in df.itertuples():
        for col in desc_cols:
            text = getattr(row, col)
            if not pd.isnull(text):
                
                yield  Description(
                    taxon=row.taxon,
                    taxon_group=row.group,
                    text=text,
                    source=col
                )
  