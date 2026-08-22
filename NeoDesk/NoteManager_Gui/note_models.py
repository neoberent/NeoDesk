
from dataclasses import dataclass
from typing import Optional
from dataclasses import dataclass
from typing import Optional

@dataclass
class Note:
    content: str           
    timestamp: str         
    owner: Optional[str] = None  
