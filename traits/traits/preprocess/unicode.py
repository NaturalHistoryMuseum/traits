from unidecode import unidecode

from adept.preprocess.preprocessor import Preprocessor


class UnicodePreproccessor(Preprocessor):
    """
    Use the unidecode library to clean special characters
    
    e.g. 5.5–33 cm × 1.4–4.7 mm => 5.5-33 cm x 1.4-4.7 mm
    """

    def preprocess(self, text):
        return unidecode(text)
        
