import typer
import pandas as pd
import spacy
from pathlib import Path
from tqdm import tqdm
import numpy as np
import warnings
import yaml
import itertools

from adept.components.registry import ComponentsRegistry
from adept.components.sentencizer import Sentencizer
from adept.components.numeric import (NumericDimension, NumericExpand, NumericFraction, NumericMeasurement, NumericRange)
from adept.components.anatomical import AnatomicalEntity
from adept.components.traits import (CustomTraitsEntity, DiscreteTraitsEntity, NumericTraitsEntity)
from adept.scripts.helpers import get_descriptions

from adept.postprocess.fields.factory import FieldFactory
from adept.postprocess.fields.discrete import DiscreteField
from adept.postprocess.aggregator import Aggregator
from adept.traits.accdb import ACCDBTraits
    
from adept.utils.doc_log import DocLog
from adept.config import logger, RAW_DATA_DIR, CORPUS_DIR
from adept.utils.helpers import get_variety_higher_taxa


def pipeline(input_path: Path, output_dir: Path, limit: int = None, taxon_group: str = None):
    
    # warnings.filterwarnings("ignore", message="CUDA is not available") 
    
    warnings.filterwarnings("ignore", message='^User provided device_type')
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    doc_log = DocLog()
    
    nlp = spacy.load("en_core_web_trf")
    registry = ComponentsRegistry(nlp)
    registry.add_components([
        Sentencizer,
        AnatomicalEntity,
        CustomTraitsEntity,
        DiscreteTraitsEntity,
        NumericTraitsEntity,
        NumericExpand,
        NumericDimension,
        NumericMeasurement,
        NumericRange,
        NumericFraction,
    ])
    
    data = {}
    accdb = ACCDBTraits()
    
    field_definitions = yaml.safe_load((CORPUS_DIR / 'fields.yaml').open())
    
    field_types = {}
    for group, fields in field_definitions.items():
        field_types[group] = {f['name']: f['type'] for f in fields}
        
    for i, description in tqdm(enumerate(get_descriptions(input_path))):
        
        # print(description.taxon)
        # if 'Crataegus wilsonii' not in description.taxon:
        #     continue
        
        # taxon_group = 'Angiosperm'
        if taxon_group and description.taxon_group.lower() != taxon_group.lower():
            continue     

        if limit and i > limit:
            break
        
        logger.info('Processing %s - %s', description.taxon, description.source)

        if description.taxon_group == 'Lichen':
            description_taxon_group = 'bryophyte'
        else:
            description_taxon_group = description.taxon_group.lower()
            
        doc = nlp(description.text)        
        DiscreteField.set_accdb_traits(doc.ents, accdb.get_terms(description_taxon_group))

        record = {
            f.get('name'): FieldFactory.factory(doc, f.copy()).as_string()
            for f in field_definitions[description_taxon_group]           
        }

        record['source'] = description.source
        record['taxon'] = description.taxon
        
        data.setdefault(description_taxon_group, []).append(record)
        
        standard_ents = ['QUANTITY', 'TRAIT', 'PART', 'CARDINAL']
        labels = {ent.label_ for ent in doc.ents}
        colour = lambda l: '#DDDDDD' if l in standard_ents else '#9AD943'
        
        colours = {label: colour(label) for label in labels}
        
        colours['PART'] = '#FFEB5D'
        options = {
            'colors': colours
        }   

        doc_log.log(doc, f'{description.taxon}-{description.source}'.lower().replace(' ', '-'), options)
        
    logger.info('Writing outout to %s', output_dir)

    for taxon_group, records in data.items():
        
        columns = ['taxon'] + [f['name'] for f in field_definitions[taxon_group]] + ['source']        
        df = pd.DataFrame(records, columns=columns)
        
        agg_dict = {f['name']: getattr(Aggregator, f"agg_{f['type'].lower()}") for f in field_definitions[taxon_group]}
        combined = df.groupby('taxon', as_index=False).agg(agg_dict)        
        combine_species_with_varieties(combined)
        
        excel_file = output_dir / f'{taxon_group}.xlsx'
        logger.info('Writing %s', excel_file) 
            
        with pd.ExcelWriter(excel_file) as writer:
            combined.to_excel(writer, sheet_name="Combined", index=False)
            for source in df.source.unique():  
                source_df = df[df.source == source]
                combine_species_with_varieties(source_df)
                source_df.to_excel(writer, sheet_name=source, index=False)        

                     
def merge(series, field_type):
    
    series_no_nan = [x for x in series.values if pd.notnull(x)]
    
    if not series_no_nan:
        return None
    
    if field_type in ['MEASUREMENT', 'VOLUME']:
        print(series)

    if series.dtype in ('int64', 'float64'):
        return min(series.values)
    else:
        return ','.join(set(itertools.chain.from_iterable(v.split(',') for v in series_no_nan)))

def combine_species_with_varieties(df):
    for i, row in df[df.taxon.str.contains('var\.|subsp\.')].iterrows():
        
        # For varieties, we want to reset plant height as it's rarely included     
        for reset_col in ['plant min. height [m]', 'plant max. height [m]']:
            df.loc[i, reset_col] = np.nan
            
        species_name = get_variety_higher_taxa(row.taxon)

        try:
            species = df[df.taxon == species_name].iloc[0]
        except IndexError:
            print('No species for ', row.taxon)
        else:
            for col, value in species[species.notna()].items():
                # Does the original have a value
                if pd.isnull(df.loc[i, col]) or df.loc[i, col] == '':
                    df.loc[i, col] = value       
      
    return df
        
        
# def write_df_to_output_dir(df, taxon_group, output_dir): 
    
#     # Ensure taxon is the first column
#     # df.insert(0, 'mean', df.pop('mean'))   
#     df = df.set_index('taxon')    
                         
#     def aggregate(cell):
        
#         _ensure_set = lambda x: x if isinstance(x, set) else set([x])

#         if cell.dtype in ['int64', 'float64']:
#             return round(cell.mean(), 2)
#         else:        
#             if combined := [_ensure_set(c) for c in cell if not pd.isnull(c)]:
#                 return set.union(*combined)
            
#         return None

#     def concat_set(df):
#         _concat = lambda x: ', '.join(x) if isinstance(x, set) else x
#         string_dtypes = df.select_dtypes(exclude=[np.number])
#         df[string_dtypes.columns] = string_dtypes.applymap(_concat)
#         return df        
    
    
    
#     combined = df.groupby('taxon').aggregate(aggregate)
#     # combined = combined.drop(columns=['source'])
#     concat_set(df)
#     concat_set(combined)  
    
#     excel_file = output_dir / f'{taxon_group}.xlsx'
#     logger.info('Writing %s', excel_file) 
        
#     with pd.ExcelWriter(excel_file) as writer:
#         combined.to_excel(writer, sheet_name="Combined")
#         for source in df.source.unique():        
#             df[df.source == source].to_excel(writer, sheet_name=source)

        
        
        # print(data)   
        
        # if taxon_group  postprocessors:
        #     break

    

        
        # columns = ['taxon', 'source'] + self._columns
        # return pd.DataFrame(self._data, columns=columns)

if __name__ == "__main__":
    typer.run(pipeline)
