 
def token_get_ent(token, ent_types=None):
    if token.ent_type_:
        for ent in token.doc.ents:
            if ent_types and ent.label_ not in ent_types: continue
            if ent.start <= token.i < ent.end:
                return ent        