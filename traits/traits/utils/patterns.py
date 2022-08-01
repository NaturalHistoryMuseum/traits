from dataclasses import dataclass, field
from typing import List, Set
from pathlib import Path
import jsonlines

@dataclass
class Patterns:
    
    _patterns: List[dict] = field(init=False, default_factory=list)
 
    def add(self, term, label, match_attr=["lower", "lemma"]):
        for match in match_attr:
            self._patterns.append(
                {
                    'label': label, 
                    'pattern': [{match: t} for t in term.split()]
                }
            )
            if '-' in term:
                self._patterns.append(
                    {
                        'label': label, 
                        'pattern': [{match: t} for t in term.split('-')]
                    }
                )
                    
    def to_jsonl(self, path: Path):
        with jsonlines.open(path, mode='w') as writer:
            writer.write_all(self._patterns)