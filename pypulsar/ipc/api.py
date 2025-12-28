
import asyncio
import json
from pypulsar.acl import acl


class Api:
    def __init__(self, engine, window_id):
        self.engine = engine
        self.window_id = window_id
        self._pending_calls = {} 

    def send(self, event: str, data: dict):
        if not acl.validate(event, data):
            print(f"[ACL] Blocked outgoing event: {event}")
            return

        message = {
            "event": event,
            "data": data,
            "window_id": self.window_id
        }
        asyncio.run_coroutine_threadsafe(
            self.engine.message_queue.put(message),
            self.engine.loop
        )

    async def pywebview_message(self, event_name: str, payload: dict = None):
        payload = payload or {}
        print(f"[PyPulsar] JS → Python API call: {event_name} {payload}")

        if not acl.validate(event=event_name, payload=payload):
            raise PermissionError(f"Event {event_name} denied by ACL")

        if not hasattr(self.engine, "api_functions"):
            raise NameError("No API functions exposed")

        if event_name not in self.engine.api_functions:
            raise NameError(f"Unknown API function: {event_name}")

        func = self.engine.api_functions[event_name]

        result = func(payload)
        if asyncio.iscoroutine(result):
            result = await result

        return result
