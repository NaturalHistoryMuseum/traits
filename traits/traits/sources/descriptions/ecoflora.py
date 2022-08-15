import pickle
import re
import requests
import urllib

from traits.sources.descriptions.description import DescriptionSource
from traits.config import CACHE_DIR
from traits.config import logger
from traits.utils.soup import Soup, RequestSoup
from traits.utils.request import CachedRequest

class EcofloraDescriptionSource(DescriptionSource):
    
    base_url = 'http://ecoflora.org.uk'
    name = 'ecoflora'

    def __init__(self):
        
        self.taxa_index = self._build_taxa_index()
        
    def get_taxon_description(self, taxon):
                    
        try:
            taxon_no = self.taxa_index[taxon]
        except KeyError:
            logger.info('Taxon %s not found in the EcoFLora taxa index', taxon)
        else:            
            return self._parse_description(taxon_no)
            
    def _parse_description(self, taxon_no):
        
        url =  f'{self.base_url}/info/{taxon_no}.html'
        try:
            soup = RequestSoup(url)
        except requests.exceptions.RequestException:
            return None
        
        if div := soup.markup.find('div', {"class": "description"}):
            # Remove the attribution para .e.g C.T.W., A.M. , C.S., B.F.
            # By ensuring the line has some lower case characters               
            ps = [p for p in div.findAll('p') if bool(re.search(r"[a-z]", p.text))]
            description = ' '.join([p.text for p in ps])
            return description
        
    def _build_taxa_index(self):

        cache_file = CACHE_DIR / 'ecoflora-taxa.pickle'
        
        try:
            f = cache_file.open('rb')
        except FileNotFoundError:
            logger.info('Rebuilding EcoFLora taxa index')
            taxa = dict(self._search_taxa())
            f = cache_file.open('wb')
            pickle.dump(taxa, f)
        else:
            logger.info('Using cached EcoFLora taxa index: %s', cache_file)
            taxa = pickle.load(f)
        finally:
            f.close()
            
        return taxa
      
    def _search_taxa(self):
        # Search page returns a list of all taxa if no parameter is supplied         
        soup = RequestSoup(f'{self.base_url}/search_synonyms.php')

        links = soup.markup.find_all('a', {'href': re.compile(r'.*search_species2.php\?plant_no=.*')})

        for link in links:
            parsed_url = urllib.parse.urlparse(link.get('href'))
            qs = urllib.parse.parse_qs(parsed_url.query)
            
            yield (link.text.strip(), qs['plant_no'][0], )
            
if __name__ == '__main__':
    src = EcofloraDescriptionSource()
    
    x = src.get_taxon_description('Achillea millefolium')
    print(x)
                
            
