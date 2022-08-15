# from .description import DescriptionSource
from .ecoflora import EcofloraDescriptionSource
from .wikipedia import WikipediaDescriptionSource
from .efloras import *


description_sources = [
    EflorasNorthAmericaDescriptionSource(),
    EflorasChinaDescriptionSource(),
    EflorasMossChinaDescriptionSource(),
    EflorasPakistanDescriptionSource(),
    EcofloraDescriptionSource(),
    WikipediaDescriptionSource()
]