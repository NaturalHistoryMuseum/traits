import requests

from adept.descriptions.description import DescriptionSource
from adept.utils.soup import Soup, RequestSoup
from adept.utils.request import CachedRequest

class WikipediaDescriptionSource(DescriptionSource):
    
    base_url = 'https://en.wikipedia.org/api/rest_v1'
    
    def get_taxon_description(self, taxon):
        page_id = self._taxon_to_page_id(taxon)
        return self.get_description(page_id)
            # print(description)
            
    @staticmethod
    def _taxon_to_page_id(taxon):
        return taxon.strip().replace(' ', '_')
    
    def get_description(self, page_id):
        url = f'{self.base_url}/page/mobile-sections/{page_id}'
        for section in self.get_page_sections(url):
            if section.get('line') == 'Description': 
                return self._extract_text_from_description(section.get('text'))

    def _extract_text_from_description(self, description):
        soup = Soup(description)
        # Remove any figures in the text
        [f.decompose() for f in soup.markup.find_all('figure')]
        return soup.markup.text
                
    def get_page_sections(self, url):
        try:
            r = CachedRequest(url); 
        except requests.exceptions.HTTPError:
            return []
            
        page_json = r.json()    
        yield from page_json['remaining']['sections'] 