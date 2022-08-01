from adept.postprocess.fields.field import Field

class NumericField(Field):
    
    def __init__(self, doc, name, part=None, require_part=True):
        super().__init__(doc, name, part, require_part) 
        self._value = self.parse_value_from_doc(doc)

    def parse_value_from_doc(self, doc):
        for sent in self.get_sents_filtered_by_part(doc):
            for ent in sent.ents:
                if ent.label_.lower() == self.name:
                    return ent._.trait_value