import time

import webview
import threading
import asyncio
import os
from aiohttp import web

class Api:
    def __init__(self, engine):
        self.engine = engine

    def send(self, params):
        event, data = params['event'], params['data']
        self.engine.js_event.emit(event, data)

class Engine:
    def __init__(self, debug=False, serve=True, port=8000, webroot="web"):
        self.js_event = asyncio.Event()
        self.py_event = asyncio.Event()
        self._webroot = webroot
        self._port = port
        self._serve = serve
        self._server = None
        self.debug = debug
        self._server_ready = None

        if serve:
            threading.Thread(target=self._start_server, daemon=True).start()
            self._wait_for_server()

    def _wait_for_server(self, timeout: float = 5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._server_ready:
                return
            time.sleep(1)

    def _start_server(self):
        async def run_server():
            app = web.Application()
            app.router.add_static('/', self._webroot)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '127.0.0.1', self._port)
            await site.start()
            self._server_ready = True
            print(f"[PyPhoton] Serving on http://127.0.0.1:{self._port}")
            while True:
                await asyncio.sleep(3600)
        asyncio.run(run_server())

    def create_window(self, path="/", title="PyPhoton", width=1000, height=600):
        url = f"http://127.0.0.1:{self._port}{path}" if self._serve else path
        api = Api(self)

        window = webview.create_window(
            title=title,
            url=url,
            width=width,
            height=height,
            js_api=api,
            on_top=False,
        )

        def on_message(message):
            # {"event": "click", "data": {...}}
            import json
            try:
                data = json.loads(message)
                self.py_event.set()
            except:
                pass
        return window

    def run(self):
        webview.start(debug=self.debug)