import itertools
import statistics
import pandas as pd

from traits.config import unit_registry

class Aggregator():
    
    # Public class methods     
    @classmethod
    def agg_discrete(cls, series):
        return cls._agg('_agg_string', series)  
    
    @classmethod
    def agg_colour(cls, series):
        return cls._agg('_agg_string', series)
    
    @classmethod
    def agg_numeric(cls, series):
        return cls._agg('_agg_numeric', series) 
    
    @classmethod
    def agg_volume(cls, series):
        return cls._agg('_agg_measurement', series) 
    
    @classmethod
    def agg_measurement(cls, series):
        return cls._agg('_agg_measurement', series)      
    
    @classmethod
    def _agg(cls, method, series):
        # Remove any NAN series         
        series = [s for s in series if pd.notnull(s)]
        
        if not series:
            return None
        elif len(series) <= 1:
            return series[0]
        
        return getattr(cls, method)(series)
                    
    @classmethod
    def _agg_string(cls, series):    
        combined_series = set(itertools.chain.from_iterable([s.split(',') for s in series]))
        return ', '.join([s for s in combined_series if pd.notnull(s) and s != ''])        
        
    @classmethod
    def _agg_measurement(cls, series):
        measurements = [unit_registry.Quantity(s) for s in series]    
        m = statistics.mean([meas.m for meas in measurements])
        units = {meas.u for meas in measurements}
        assert(len(units) == 1)
        return unit_registry.Quantity(m, units.pop())
    
    @classmethod
    def _agg_numeric(cls, series):    
        try:
            return statistics.mean([float(s) for s in series if pd.notnull(s) and s != ''])
        except Exception:
            print('NUMERIC ERROR:', series)
            return series 