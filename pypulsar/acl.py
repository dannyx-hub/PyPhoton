import re
from typing import Callable, Dict, List, Any, Optional
from functools import wraps


class ACL:
    def __init__(self):
        self.rules: Dict[str, List[re.Pattern]] = {}
        self.validators: Dict[str, Callable[[dict], bool]] = {}

    def allow(self, event_pattern: str):
        if not event_pattern.startswith("^"):
            event_pattern = "^" + re.escape(event_pattern) + "$"
        pattern = re.compile(event_pattern)
        self.rules.setdefault("allow", []).append(pattern)

    def deny(self, event_pattern: str):
        if not event_pattern.startswith("^"):
            event_pattern = "^" + re.escape(event_pattern) + "$"
        pattern = re.compile(event_pattern)
        self.rules.setdefault("deny", []).append(pattern)

    def validate(self, event: str, payload: dict) -> bool:
        if self.rules.get("deny"):
            for pat in self.rules["deny"]:
                if pat.fullmatch(event):
                    return False
        if self.rules.get("allow"):
            for pat in self.rules["allow"]:
                if pat.fullmatch(event):
                    validator = self.validators.get(event) or self.validators.get(pat.pattern)
                    if validator and not validator(payload):
                        return False
                    return True
        return False

    def validator(self, event_pattern: str):
        if not event_pattern.startswith("^"):
            pattern = "^" + re.escape(event_pattern) + "$"
        else:
            pattern = event_pattern
        def decorator(func: Callable[[dict], bool]):
            nonlocal pattern
            self.validators[pattern] = func
            @wraps(func)
            def wrapper(payload: dict) -> bool:
                return func(payload)
            return wrapper
        return decorator

acl = ACL()