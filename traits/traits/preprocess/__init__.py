from .abbreviations import AbbreviationsPreproccessor
from .conjoined import ConjoinedPreproccessor
from .unicode import UnicodePreproccessor

preprocessors = [
    AbbreviationsPreproccessor(),
    ConjoinedPreproccessor(),
    UnicodePreproccessor()
]