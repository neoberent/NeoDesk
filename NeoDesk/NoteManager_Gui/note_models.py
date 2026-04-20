
from dataclasses import dataclass
from typing import Optional
from dataclasses import dataclass
from typing import Optional

@dataclass
class Note:
    """
    Repräsentiert eine Notiz mit Inhalt, Zeitstempel und optionalem Besitzer.
    """
    content: str           
    timestamp: str         
    owner: Optional[str] = None  
