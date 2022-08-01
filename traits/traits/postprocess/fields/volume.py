from adept.postprocess.fields.measurement import MeasurementField

from spacy.tokens import Span, Doc

class VolumeField(MeasurementField): 
    def parse_value_from_doc(self, doc: Doc):
        for sent in self.get_sents_filtered_by_part(doc):
            if sent._.volume_measurements:
                self.parse_measurement_value(sent._.volume_measurements)                
                break   