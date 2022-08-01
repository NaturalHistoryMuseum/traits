
from click import pass_context
import pandas as pd
import pandas_access as mdb
import pandas as pd
import uuid
import numpy as np
import itertools


# FIXME: This is all much better as a dataframe

from adept.config import RAW_DATA_DIR

class ACCDBTraits():
    """ 
    Read the traits from functional traits CCDB
    """
    
    accdb_file_path = RAW_DATA_DIR / 'Functional Traits_Working_File.accdb'
    plant_groups = ['angiosperm', 'bryophyte', 'pteridophyte']
    plants_group_col = 'Plants Group'      
    
    def __init__(self):
        self._df = self._get_traits_df()
    
    def get_plant_group(self, plant_group):  
        return self._df[self._df[self.plants_group_col] == plant_group]       
        
    def get_unique_terms(self, plant_group = None):  
        df = self.get_terms(plant_group)
        return df.term.unique()
    
    def get_colours(self, plant_group = None):
        df = self.get_terms(plant_group)
        return set(itertools.chain.from_iterable(df[df.trait.str.contains('colour')][['term', 'character']].values))
        
    def get_terms(self, plant_group = None):  
        df = self.get_plant_group(plant_group) if plant_group else self._df        
        # We use term, character and synonyms (exploded) to get trait terms
        cols = ['character', 'trait', self.plants_group_col]
        return pd.concat(
            [
                df[['term'] + cols],
                df[df.synonym.notnull()].explode('synonym')[['synonym'] + cols].rename(columns={'synonym': 'term'})
            ], ignore_index=True
        ).drop_duplicates()
                        
    def _get_traits_df(self):
        
        synonyms_df = self._get_synonyms_df()
      
        dfs = [self._get_plant_group_df(plant_group) for plant_group in self.plant_groups]                
        df = pd.concat(dfs, ignore_index=True)
        
        # gymnosperms are the same as angiosperms, so AC has just added a few extra gymnosperm-only traits 
        # Copy the angiosperm traits, and set plant group to gymnosperm
        gymnosperm_df = df[df[self.plants_group_col] == 'angiosperms'].copy()
        gymnosperm_df[self.plants_group_col] = 'gymnosperm'  
        
        df.append(gymnosperm_df, ignore_index=True)
        df = df.rename(columns={"Trait 4": "trait4"}) 
                
        df['uuid'] = df.apply(lambda _: uuid.uuid4(), axis=1)
        
        char_trait_cols = ["character", "trait"]
        
        # Stack the table so all characterX and traitX columns are
        # combined into character and trait column
        df = pd.wide_to_long(df, char_trait_cols, i='uuid', j="x")
        
        df = df[['termID', 'term', 'character', 'trait', self.plants_group_col]]
        
        synonyms_df.synonym = synonyms_df.synonym.replace('_','-', regex=True)
        synonyms_df = synonyms_df.groupby('term')['synonym'].apply(set).reset_index().set_index('term')        
        df = df.join(synonyms_df, 'term', 'left')        
        
        # If char and trait are empty, the row probably didn't have trait2, trait3 etc., set
        df = df.dropna(subset=char_trait_cols)                
        
        term_cols = ['term', 'character', 'trait']
        df[term_cols] = df[term_cols].replace('_','-', regex=True)
        df[term_cols] = df[term_cols].applymap(self._normalise_text)
                
        # missing = pd.DataFrame([
        #     {'term': 'stem erect', 'character': 'stem erect', 'trait': 'habit', 'Plants Group': 'angiosperm'
        # }])
        
        excel_terms = self._get_excel_terms_df()

        df = df.append(excel_terms, ignore_index=True)
   
        return df       
        
    
    def _get_synonyms_df(self):
        df = self._accdb_read_table('plant_glossary_synonyms')
        # We only want term and synonym
        df = df[['term', 'synonym']].drop_duplicates()        
        return df
    
    def _get_excel_terms_df(self):
        data = []
        xls = pd.ExcelFile(RAW_DATA_DIR / 'functional-trait-list.xlsx')

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(RAW_DATA_DIR / 'functional-trait-list.xlsx', sheet_name=sheet_name)
            taxon_group = sheet_name.replace('traits', '').strip().lower()
            for col in df.columns:
                values = df[col].dropna().unique()
                if len(values) > 2:
                    for value in values:
                        data.append({
                            'term': value, 
                            'character': value, 
                            'trait': col.lower(),
                            'Plants Group': taxon_group
                        }) 
        return data           
                
    def _get_plant_group_df(self, plant_group):
        table_name = f'{plant_group}_traits' 
        df = self._accdb_read_table(table_name)
        df[self.plants_group_col] = plant_group        
        
        return df
                
    def _accdb_read_table(self, table_name):
        return mdb.read_table(self.accdb_file_path, table_name)
        
    @staticmethod
    def _normalise_text(text):

        missplellings = [
            ('polination', 'pollination'),
            ('pilosity_surface', 'pilosity - surface'),
            ('leaf apex\r\nleaf apex\trecurved', 'leaf apex'),
            ('fruit type\r\nfruit type\tfollicle', 'fruit type'),
            ('pernnial organ', 'perennial organ'),
            ('leas apex', 'leaf apex'),
            ('leas base', 'leaf base'),
            ('leaf arraangement', 'leaf arrangement')                   
        ]
        if type(text) == str:
            text = text.lower()
            for err, corr in missplellings:
                if text == err: text = corr

        return text
        
   
if __name__ == '__main__':
    t = ACCDBTraits()
    # angiosperm = t.get_traits()
    # print(angiosperm)
    
