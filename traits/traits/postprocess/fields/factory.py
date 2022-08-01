from adept.postprocess.fields.colour import ColourField
from adept.postprocess.fields.discrete import DiscreteField
from adept.postprocess.fields.measurement import MeasurementField
from adept.postprocess.fields.numeric import NumericField
from adept.postprocess.fields.volume import VolumeField


class FieldFactory(object):
    
    classes = {
        'colour': ColourField,
        'discrete': DiscreteField,
        'measurement': MeasurementField,
        'numeric': NumericField,
        'volume': VolumeField,
    }
    
    @classmethod
    def factory(cls, doc, field_dict):
        field_type = field_dict.pop('type', 'DISCRETE').lower()
        return cls.classes[field_type](doc, **field_dict)