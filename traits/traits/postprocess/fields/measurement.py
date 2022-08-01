import re
from spacy.tokens import Span, Doc


from adept.postprocess.fields.field import Field
from adept.config import unit_registry

class MeasurementField(Field):
    
    # Length/height measurements are provided first, followed by width. 
    dimension_axes = ['y', 'x']  
    require_sent_part = True
    
    def __init__(self, doc: Doc, name: str, part=None, require_part=True):
        super().__init__(doc, name, part, require_part) 
        self.unit = None
        self.parse_value_from_doc(doc)
        
    @property
    def value(self):
        return self.get_converted_value()
    
    def as_string(self):   
        if self.value:
            return format(self.value, '~')    
    
    def parse_value_from_doc(self, doc):
        for sent in self.get_sents_filtered_by_part(doc):
            if sent._.dimensions:
                self.parse_dimension_value(sent._.dimensions[0])
                break
            elif sent._.measurements:
                self.parse_measurement_value(sent._.measurements)                
                break
                        
    def parse_dimension_value(self, dimension):

        for i in range(0,2):
             # 0 => 1; 1 => 0
            adj_i = (i-1)**2

            ent = dimension.ents[i]
            axis = self.dimension_axes[i]
            # Sometimes the unit is only attached to one of the dimensions e.g. 1.5-2 x 1.7-2.2 cm             
            unit = ent._.measurement_unit or dimension.ents[adj_i]._.measurement_unit
            self.set_value(axis, ent, unit)

    
    def parse_measurement_value(self, measurements):
        # If we have two measurements, treat them as y, x         
        if len(measurements) == 2:
            for axis, measurement in zip(self.dimension_axes, measurements):
                self.set_value(axis, measurement, measurement._.measurement_unit)
                
        # FIXME: If we only have one measurement, default to the one expected by the field          
        elif len(measurements) == 1:
            measurement = measurements[0]
            # Default to the field axis             
            self.set_value(self.field_axis, measurement, measurement._.measurement_unit)

    def set_value(self, axis, ent, unit):
        
        # Some measurements are detected, but have no unit. 
        # E.g. Petals white, suborbicular, 6-7 x 5-6.
        # No unit = do not use the measurement
        if not unit:
            return

        if axis == self.field_axis:
            value_dict = self._get_ent_value(ent)
            unpack = lambda ks: ([v for k in ks if (v := value_dict.get(k))])
            if self.is_minimum:
                self._value = min(unpack(['lower', 'from']), default=None)
            elif self.is_maximum:
                self._value = max(unpack(['to', 'upper']), default=None)
            else:
                raise Exception('Not min or max')

            self.unit = unit
            
    def get_converted_value(self):
        if self._value:
            try:
                measurement = float(self._value) * self.unit
            except:
                print(self.unit)
                print(self.name)
                raise
            converted_value = measurement.to(self.target_unit) 
            return round(converted_value, 2)        
                        
    @property
    def field_axis(self):
        # length, height and depth are y; width is x axis         
        return 'x' if 'width' in self.name else 'y'
    
    @property
    def target_unit(self):
        if match := re.search('\[([a-z³]+)\]', self.name):
            unit = match.group(1)
            return unit_registry(unit)
        
    @property
    def is_minimum(self):
        # Does the field name contain min.         
        return re.search('\smin.', self.name)      
    
    @property
    def is_maximum(self):
        # Does the field name contain max.         
        return re.search('\smax.', self.name)      
    
    @staticmethod
    def _get_ent_value(ent: Span):
        if ent._.numeric_range:
            value = ent._.numeric_range
        else:

            # Also validate shape is d, dd, so cast to int won't fail
            num = [int(token.text) for token in ent if token.pos_ == 'NUM' and set(token.shape_) == set('d')]
            value = {'from': min(num, default=None), 'to': max(num, default=None)} 
   
        return value     