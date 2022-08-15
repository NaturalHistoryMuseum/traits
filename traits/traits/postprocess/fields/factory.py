from .colour import ColourField
from .discrete import DiscreteField
from .measurement import MeasurementField
from .numeric import NumericField
from .volume import VolumeField


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