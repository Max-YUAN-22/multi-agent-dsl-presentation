
from __future__ import annotations
from typing import Any, Dict, Optional, List
import json, re

class Contract:
    """Lightweight output contract: regex + minimal JSON 'required' validation."""
    def __init__(self, name: str, schema: Optional[Dict]=None, regex: Optional[str]=None):
        self.name = name
        self.schema = schema or {}
        self.regex = re.compile(regex) if regex else None

    def validate(self, text: str) -> bool:
        if self.regex and not self.regex.fullmatch(text or ''):
            return False
        req: List[str] = list(self.schema.get('required', []))
        if req:
            try:
                obj = json.loads(text)
                if not isinstance(obj, dict):
                    return False
                for k in req:
                    if k not in obj:
                        return False
            except Exception:
                return False
        return True
