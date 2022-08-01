import re

from adept.preprocess.preprocessor import Preprocessor


class AbbreviationsPreproccessor(Preprocessor):

    # https://books.google.co.uk/books?id=PoUWAAAAYAAJ&pg=PA128&lpg=PA128&dq=botany+abbreviations+Lvs&source=bl&ots=F2x92m2CMy&sig=ACfU3U3Ptjqi8FpARJirXjnahtCzreg-qA&hl=en&sa=X&ved=2ahUKEwjUiaaq_-vsAhUNesAKHU-KDfQ4ChDoATAFegQIAxAC#v=onepage&q=botany%20abbreviations%20Lvs&f=false

    abbrv = {
        'lf': 'leaf',
        'lvs': 'leaves',
        'lfless': 'leafless',
        'fl': 'flower',
        'fls': 'flowers',
        'fr': 'fruit',
        'frt': 'fruit',
        'frts': 'fruits',
        'sds': 'seeds',
        'fil': 'filaments',
        'pet': 'petals',
        'infl': 'inflorescence',
        'inf': 'inflorescence',
        'fld': 'flowered',
        'lflets': 'leaflets',
        'lflet': 'leaflet',
        'lfy': 'leafy',
        'lngth': 'length',
        'diam': 'diameter',
    }

    def __init__(self):
        self._re_abbreviations = re.compile(r'(?=\-|\b)(%s)(?=\s|$|[:,\-\.])' % '|'.join(
            [f'{k}' for k in self.abbrv.keys()]
        ), re.IGNORECASE)
        self._sentence_end_commas = re.compile(r',(\s+[A-Z])')        

    def preprocess(self, text):
        text = self._replace_abbreviations(text)
        text = self._remove_double_spaces(text)
        text = self._remove_double_dashes(text)
        text = self._replace_long_dashes(text)
        text = self._replace_sentence_end_commas(text)
        return text

    def _replace_abbreviations(self, text):
        
        def _get_sub_text(match):
            match_text = match.group(1)          
            sub_text = self.abbrv.get(match_text.lower().rstrip('.'), match_text)
            if match_text[0].isupper(): sub_text = sub_text.capitalize()
            return sub_text

        # Pattern: \b(fl\.?|lvs\.?)(?=\s|$)
        # Remove the dot afterwards '{k}\.?' Might need to check for following uppercase char??
        return self._re_abbreviations.sub(_get_sub_text, text)
  
    def _remove_double_spaces(self, text):
        # Quicker than regex - https://stackoverflow.com/questions/1546226/is-there-a-simple-way-to-remove-multiple-spaces-in-a-string
        return " ".join(text.split())

    def _remove_double_dashes(self, text):
        return text.replace('--', '-')
    
    def _replace_long_dashes(self, text):
        return text.replace('–', '-')  
       
    def _replace_sentence_end_commas(self, text):
        # Replace sentences ending in a comma xxx, Y => xxx. Y
        # E.g. An erect, glabrous, stoloniferous or rhizomatous perennial, 30-60 cm, Stems ... 
        return self._sentence_end_commas.sub(r'.\1', text)   


if __name__ == '__main__':

    d = 'Lf-blades 5-15 (-20) mm, orbicular or obovate-orbicular, rounded at both ends, deeply and regularly crenate, glabrous at maturity;'        

    preproccessor = AbbreviationsPreproccessor()
    text = preproccessor(d)
    print(text)
