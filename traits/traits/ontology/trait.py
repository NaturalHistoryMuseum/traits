import pandas_access as mdb
import pandas as pd

from adept.config import RAW_DATA_DIR


# class SourceFactory(object):
    
#     def factory(source_name, source_type):
#         for cls in Source.get_subclasses():
#             if cls.name == source_name and cls.source_type.name.lower() == source_type:
#                 return cls

#     factory = staticmethod(factory)   
    
# plant_groups = list['Angiosperms']

# These traits are too generalised, so we need to use the
# catagory for greater specificity
non_specific_traits = ['leaf architecture']

class Trait():
    def __init__(self, name, group, category):
        name = name.lower() 
        category = category.lower()
        
        # Is this a leaf part?
        if name in non_specific_traits and name != category:
            name = f'{name} - {category}'
        self.name = name
        self.category = category
        self.group = group
        
 
leaf_architecture = Trait('Leaf architecture', 'Angiosperms', 'conduplicate')
leaf_architecture.add_character('conduplicate', 'v-form');

   
# Filter by - Leaf architecture 

# Loop through all characters, and see if there's a plant part??


    
    
    
class TraitOntology():
   
    accdb = RAW_DATA_DIR / 'Functional Traits_Working_File.accdb'
    taxa_group = ['angiosperm']
    
    def __init__(self):        
        
        dfs = []
        for group in self.taxa_group:   
            table_name = f'{group}_traits'                 
            df = mdb.read_table(self.accdb, table_name)
            
            # df.set_index('term', verify_integrity=True)
            
            for idx, row in df.iterrows():
                
                char_traits = [
                    (char, trait) for x in range(1,3) if (trait := row.get(f'trait{x}')) and (char := row.get(f'character{x}'))
                ]
                
                # print(i)
                
                print(row.get('trait1'))
                print(row['character1'])
                print(char_traits)
                
            
            
            # print(df.head())
            # Replace underscores with -
            # df.term.replace(regex=r'_', value='-', inplace=True)
            # df.term = df.term.str.lower()
            # df.group = group
            # dfs.append(df)
            
        # self.df = pd.concat(dfs)        

    @property
    def terms(self):
        return set(self.df.term.unique())


if __name__ == '__main__':
    TraitOntology()