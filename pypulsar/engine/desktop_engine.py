import time
import asyncio
from aiohttp import web
import webview
from pypulsar.engine.base_engine import BaseEngine, Hooks


class DesktopEngine(BaseEngine):
    def _run_server_processor(self):
        async def server_task(self):
            self.loop = asyncio.get_event_loop()
            app = web.Application()
            app.router.add_static("/", path=self._webroot)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", self._port)
            await site.start()
            self._server_ready = True
            print(f"[PyPulsar] Server started -> htpp://127.0.0.1:{self._port}")
            await self._start_message_processor()
            while True:
                await asyncio.sleep(3600)
        asyncio.run(server_task(self))

    def run(self):
        self.emit_hook(Hooks.ON_APP_START)
        webview.start(debug=self.debug, http_server = not self._serve)
        
        