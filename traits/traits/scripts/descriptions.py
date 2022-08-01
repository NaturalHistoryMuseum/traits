import click
import pandas as pd
import numpy as np
import typer
from pathlib import Path

from adept.descriptions import sources
from adept.utils.helpers import get_variety_higher_taxa
    
# @click.command()
# @click.argument('output_path', type=click.Path())
# @click.option('-t', '--taxa_path', type=click.Path())
def main(taxa_path: Path, output_path: Path):
    
    taxon_name_col = 'Species name'
    
    df = pd.read_csv(taxa_path, converters={taxon_name_col: str.strip})
    
    # FIXME: A value is trying to be set on a copy of a slice from a DataFrame.
    # Ensure all variety higher species is included
    var_species = df[df['Species name'].str.contains('var\.|subsp\.')].loc[:]
    var_species['Species name'] = var_species['Species name'].apply(get_variety_higher_taxa)
    
    df = df.append(var_species).drop_duplicates()    
    
    for source in sources:   
        df[source.name] = df[taxon_name_col].apply(source.get_taxon_description)
    
    df = df.rename(
        columns={
            taxon_name_col: 'taxon',
            'Major group': 'group',
            'Family': 'family',
            }
        )
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # Output some nice stats
    source_names = [source.name for source in sources]
    
    df['any'] = ~pd.isnull(df[source_names]).all(1)

    df.replace(to_replace=False, value=np.NAN, inplace=True, method=None) 

    print(df[source_names + ['taxon', 'group', 'any']].groupby('group').count())   
    

    

if __name__ == '__main__':
    typer.run(main)