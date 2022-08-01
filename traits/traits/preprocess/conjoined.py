import re

from adept.preprocess.preprocessor import Preprocessor


class ConjoinedPreproccessor(Preprocessor):

    # Split numeric values from text
    def __init__(self):
        self._re_conjoined_numeric = [
            re.compile(r'([a-z])([\d])'), # a1 => a 1
            re.compile(r'(?!2n)([\d])([a-z])') # 1a => 1 a (but excluding 2n)       
        ]
        self._re_conjoined_punct = re.compile(r'(?<=\D)([,.])(?=\S)')              
        
    def preprocess(self, text):
        text = self._split_conjoined_numeric(text)
        text = self._split_conjoined_punct(text)
        return text
        
    def _split_conjoined_punct(self, text):
        # Add a space after a dot or comma, if it doesn't exist and is not part of a digit
        return self._re_conjoined_punct.sub(r'\1 ', text)
    
    def _split_conjoined_numeric(self, text):
        
        for re_ in self._re_conjoined_numeric:
            text = re_.sub(r'\1 \2', text)
            
        return text        
 


if __name__ == '__main__':

    d = 'Ray florets8-10(-13), 2cm and sterile'        

    preproccessor = ConjoinedNumericPreproccessor()
    text = preproccessor(d)
    print(text)
