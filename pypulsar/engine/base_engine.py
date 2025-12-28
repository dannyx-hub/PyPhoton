from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Optional, Dict, Callable, Any

from pypulsar.acl import acl
from pypulsar.window_manager import WindowManager
from pypulsar.ipc.api import Api
from pypulsar.plugins.plugin_manager import PluginManager

class Hooks:
    ON_APP_START = "on_app_start"
    ON_WINDOW_CREATE = "on_window_create"
    ON_EVENT =  "on_event"
    
class BaseEngine(ABC):
    """
    An abstract base for engines in PyPulsar.
    It defines a common API for managing the application, windows, hooks, plugins, and communication.
    Concrete engines (e.g., DesktopEngine, AndroidEngine) inherit from it and implement
    platform-specific methods (such as _create_window_impl and run).
    """

    def __init__(self, debug: bool = False, serve: bool = True, port: int = 8080, webroot: str = "web"):
        self.debug = debug
        self._serve = serve
        self._port = port
        self._webroot = webroot
        self._server_ready = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.child_windows = []
        self.parent_window = None
        self.window_manager = WindowManager(self, Hooks)
        self.message_queue = asyncio.Queue()
        self.hooks: Dict[str, list[Callable]] = {value : [] for key, value in Hooks.__dict__.items() if not key.startswith("__")}
        
        self.plugins = PluginManager()
        self.plugins.set_engine(self)
        self.plugins.discover_plugins()
        
        
        if serve:
            threading.Thread(target=self._run_server_processor, daemon=True).start()
            self._wait_for_server()
        else:
            self.loop = asyncio.get_event_loop()
            
    def register_hook(self, hook_name: str, callback: Callable):
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
                    print(f"[PyPulsar] Hook error {hook_name} - {e}")
            threading.Thread(target=run, daemon=True).start()
    
    def _wait_for_server(self, timeout: float = 8.0):
        import time
        deadline = time.time() + timeout
        while time.time() < deadline and not self._server_ready:
            time.sleep(0.1)
        if not self._server_ready:
            raise TimeoutError(f"[PyPulsar] Server not start in {self._port}")
        
    @abstractmethod
    async def _run_server_processor(self):
        """
        Abstract method for starting the server (e.g., aiohttp) and the message processor.
        The implementation depends on the platform (e.g., using aiohttp on desktop, and something else on mobile).
        """
        pass
     
    async def _start_message_processor(self):
        print("[PyPulsar]  Message processor started")
        while True:
            try:
                message = await self.message_queue.get()
                event_name = message.get("event")
                data = message.get("data")
                window_id = message.get("window_id")
                print(f"[PyPulsar] Get event {event_name}")
                self.emit_hook(Hooks.ON_EVENT, event_name, data, window_id)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[PyPulsar] Message error: {e}")
                
    def create_window(self, path: str = "/", title: str = "PyPulsar", width: int = 1000, height: int = 700, resizable: bool = True):
        url = f"http://127.0.0.1:{self._port}{path}" if self._serve else path
        return self.window_manager.create_window(is_main=True, url=url, title=title, width=width, height=height, resizable=resizable)
    
    def create_child_window(self, path: str = "/", title: str = "PyPulsarChild", width: int = 500, height: int = 350, resizable: bool = True):
        url = f"http://127.0.0.1:{self._port}{path}" if self._serve else path
        return self.window_manager.create_window(is_main=False, url=url, title=title, width=width, height=height, resizable=resizable)
    
    def close_window(self, window_id: str):
        self.window_manager.close_window(window_id=window_id)
        
    def send_to_window(self, window_id: str, js_code: str):
        self.window_manager.evaluate_js(window_id=window_id, js_code=js_code)
        
    def get_window(self, window_id: str):
        return self.window_manager.get_window(window_id=window_id)
    
    @abstractmethod
    def run(self):
        """
        Abstract method for starting the application (event loop, main window, etc.).
        The implementation is platform-specific (e.g., `webview.start()` on desktop, `toga.App.run()` on mobile).
        """
        pass
    
    def quit(self):
        windows = self.window_manager.windows
        for window in windows:
            window.destroy()
    
    
    