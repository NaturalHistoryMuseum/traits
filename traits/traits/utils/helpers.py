import re

def get_variety_higher_taxa(name):
    # Regex to match species name before var. or subsp.  
    return re.match('^[a-zA-Z\s]+(?=(\svar\.|\ssubsp\.))', name).group(0)