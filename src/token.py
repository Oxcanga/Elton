from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
