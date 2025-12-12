# pypulsar/engine.py
import time
import asyncio
import threading
from aiohttp import web
import webview
import os
from pypulsar.acl import acl

class Hooks:
    ON_APP_START = "on_app_start"
    ON_WINDOW_CREATE = "on_window_create"
    ON_EVENT = "on_event"


class Api:
    def __init__(self, engine):
        self.engine = engine

    def send(self, params):
        if not isinstance(params, dict) or "event" not in params:
            print("[PyPulsar] Error: api.send() require {event, data}")
            return

        # Wrzucamy całą wiadomość do kolejki w Pythonie
        asyncio.run_coroutine_threadsafe(
            self.engine.message_queue.put(params),
            self.engine.loop
        )


class Engine:
    def __init__(self, debug=False, serve=True, port=8000, webroot="web"):
        self.debug = debug
        self._serve = serve
        self._port = port
        self._webroot = webroot
        self._server_ready = False
        self.loop = None

        self.message_queue = asyncio.Queue()

        self.hooks = {value: [] for key, value in Hooks.__dict__.items()
                      if not key.startswith("__")}

        from pypulsar.plugins.plugin_manager import PluginManager
        self.plugins = PluginManager()
        self.plugins.set_engine(self)
        self.plugins.discover_plugins()

        if serve:
            threading.Thread(target=self._run_server_and_processor, daemon=True).start()
            self._wait_for_server()
        else:
            self.loop = asyncio.get_event_loop()

    def register_hook(self, hook_name, callback):
        if hook_name in self.hooks:
            self.hooks[hook_name].append(callback)
        else:
            raise ValueError(f"Unknown hook: {hook_name}")

    def emit_hook(self, hook_name, *args, **kwargs):
        if hook_name not in self.hooks:
            return

        for callback in self.hooks[hook_name]:
            def run():
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"[PyPulsar] Hook error {hook_name}: {e}")
            threading.Thread(target=run, daemon=True).start()

    def _wait_for_server(self, timeout: float = 8.0):
        deadline = time.time() + timeout
        while time.time() < deadline and not self._server_ready:
            time.sleep(0.1)
        if not self._server_ready:
            raise TimeoutError(f"[PyPulsar] Server not start on {self._port}")

    def _run_server_and_processor(self):
        async def main():
            self.loop = asyncio.get_running_loop()

            app = web.Application()
            app.router.add_static('/', path=self._webroot)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '127.0.0.1', self._port)
            await site.start()
            self._server_ready = True
            print(f"[PyPulsar] Server started → http://127.0.0.1:{self._port}")

            await self._start_message_processor()

            while True:
                await asyncio.sleep(3600)

        asyncio.run(main())

    async def _start_message_processor(self):
        print("[PyPulsar] Message processor started")
        while True:
            try:
                message = await self.message_queue.get()
                event_name = message.get("event")
                data = message.get("data", {})

                print(f"[PyPulsar] Get event: {event_name}")
                self.emit_hook(Hooks.ON_EVENT, event_name, data)

                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[PyPulsar] Message Error: {e}")

    def create_window(self, path="/", title="PyPulsar", width=1000, height=700, resizable=True):
        if self._serve:
            url = f"http://127.0.0.1:{self._port}{path}"
        else:
            url = f"file://{os.path.abspath(os.path.join(self._webroot, path.lstrip('/')))}"

        api = Api(self)

        window = webview.create_window(
            title=title,
            url=url,
            width=width,
            height=height,
            resizable=resizable,
            js_api=api,
            text_select=True,
        )

        @window.expose
        def pywebview_message(event: str, data=None):
            if data is None:
                data = {}
            if not acl.validate(event, data):
                print(f"[ACL] Event Banned {event}")
                window.evaluate_js(f"console.warn('ACL: Event Banned {event}')")
                return
            message = {"event": event, "data": data}
            asyncio.run_coroutine_threadsafe(
                self.message_queue.put(message),
                self.loop
            )

        self.emit_hook(Hooks.ON_WINDOW_CREATE, window)
        return window

    def run(self):
        self.emit_hook(Hooks.ON_APP_START)
        webview.start(debug=self.debug, http_server=not self._serve)

    # def quit(self):
    #     webview.destroy_all_windows()