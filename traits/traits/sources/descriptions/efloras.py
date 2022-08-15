import enum
import requests
import urllib.parse
import re
from abc import ABCMeta, abstractmethod, ABC

from traits.sources.accdb import ACCDBTraits
from traits.utils.enum import Enum
from traits.utils.soup import Soup, RequestSoup
from traits.utils.request import CachedRequest
from traits.config import logger
from traits.sources.descriptions.description import DescriptionSource


class EflorasDescriptionSource(DescriptionSource):
    base_url = 'http://efloras.org'
    
    class Floras(enum.Enum, metaclass=Enum):
        FLORA_OF_NORTH_AMERICA = 1
        FLORA_OF_CHINA = 2            
        MOSS_FLORA_OF_CHINA = 4
        FLORA_OF_PAKISTAN = 5 
     
        
    @property
    @abstractmethod
    def flora_id(self: Floras):
        pass          
             
    @property
    def name(cls):
        return cls.flora_id.name.lower()
    
    def __init__(self):
        super().__init__()  
        
        accdb = ACCDBTraits()
        self.terms = accdb.get_unique_terms()  
            
    def get_taxon_description(self, taxon_name):
                
        taxon_id = self.search(taxon_name)

        if taxon_id: 
            
            return self._parse_description(self.flora_id, taxon_id)

    
    def search(self, taxon_name):

        url =  f'{self.base_url}/browse.aspx'

        try:
            # We use flora_id = 0 to search for all, which is 
            # then cached for all floras - too slow otherwise
            soup = RequestSoup(url, flora_id=0, name_str=taxon_name)
        except requests.exceptions.RequestException:
            return None   
        
        search_results = self._parse_query_page(soup)
        
        try:
            return search_results[self.flora_id.value]
        except KeyError:
            logger.debug('No results for %s - %s', taxon_name, self.flora_id)
        
    def _parse_query_page(self, soup):
        
        search_results = {}
        
        title_span = soup.markup.find("span", {"id": "ucFloraTaxonList_lblListTitle"}) 
        
        if title_span.get_text(strip=True) == 'No taxa found':
            logger.info('No taxa found: %s', soup.parametised_url)
            return {}
        
        div = soup.markup.find("div", {"id": "ucFloraTaxonList_panelTaxonList"})        
        
        # We specify title="Accepted name" to exclude synonyms
        for a in div.find_all("a", href=re.compile("^florataxon"), title="Accepted Name"):        
            parsed_url = urllib.parse.urlparse(a.get('href'))
            qs = urllib.parse.parse_qs(parsed_url.query) 
            search_results[int(qs['flora_id'][0])] = int(qs['taxon_id'][0]) 
        
        return search_results
        
    def _parse_description(self, flora_id, taxon_id):
        url = f'{self.base_url}/florataxon.aspx'  
        try:      
            soup = RequestSoup(url, flora_id=flora_id.value, taxon_id=taxon_id)
        except Exception as e:
            logger.error('Requests exception: %s', e)
            return
        
        taxon_treatment = soup.markup.find('div', {'id': 'panelTaxonTreatment'})   
        
        if not taxon_treatment:
            logger.error('No taxon treatment: %s', soup.parametised_url) 
            return          
        
        p_text = [p.get_text() for p in taxon_treatment.find_all('p') if p.get_text(strip=True) and not p.find('table')]
        
        descriptions = [p for p in p_text if self._is_plant_description(p)]

        if descriptions:
            if len(descriptions) > 1:
                logger.debug('Multiple treatment paragraphs %s', soup.parametised_url)
                
            return '\n'.join(descriptions)
            
        
    # FIXME: This is just horrible. Train a text classifier to do this!
    def _is_plant_description(self, text):
        plant_part_words = self.words_in_string(self.terms, text) 
        if plant_part_words:     
            perentage = len(plant_part_words) / len(text.split())
            # If the percentage of parts is greater than 5% (for short descriptions)
            if perentage >= 0.05 or len(plant_part_words) >= 3:
                return True
            
    @staticmethod        
    def words_in_string(word_list, description):
        # Remove punctuation and split string into words
        words = re.sub("[^\w\s]", "", description).lower().split()

        return set(word_list).intersection(words)    
    
    
class EflorasNorthAmericaDescriptionSource(EflorasDescriptionSource):
    
    flora_id = EflorasDescriptionSource.Floras.FLORA_OF_NORTH_AMERICA
        
class EflorasChinaDescriptionSource(EflorasDescriptionSource):
    
    flora_id = EflorasDescriptionSource.Floras.FLORA_OF_CHINA
        
class EflorasPakistanDescriptionSource(EflorasDescriptionSource):
    
    flora_id = EflorasDescriptionSource.Floras.FLORA_OF_PAKISTAN  
    
class EflorasMossChinaDescriptionSource(EflorasDescriptionSource):
    
    flora_id = EflorasDescriptionSource.Floras.MOSS_FLORA_OF_CHINA       
        
if __name__ == '__main__':
    src = EflorasNorthAmericaDescriptionSource()
    
    x = src.get_taxon_description('Achillea millefolium')
    print('SSS')
    print(x)    