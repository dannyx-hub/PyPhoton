import os
import json
import importlib.util

class Plugin:
    def __init__(self, path):
        self.path = path
        self.manifest = {}
        self.module = None

    def load_manifest(self):
        manifest_path = os.path.join(self.path, "plugin.json")
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(manifest_path)
        with open(manifest_path, "r") as f:
            self.manifest = json.load(f)

    def load_module(self):
        entry_path = os.path.join(self.path, self.manifest["entry"])
        spec = importlib.util.spec_from_file_location(self.manifest["name"], entry_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.module = module

    def register(self, engine):
        if hasattr(self.module, "register"):
            self.module.register(engine)


class PluginManager:
    def __init__(self, plugin_folder="plugins"):
        self.engine = None
        self.plugin_folder = plugin_folder
        self.plugins = []

    def set_engine(self, engine):
        self.engine = engine

    def discover_plugins(self):
        if not os.path.exists(self.plugin_folder):
            os.makedirs(self.plugin_folder)
        for item in os.listdir(self.plugin_folder):
            path = os.path.join(self.plugin_folder, item)
            if os.path.isdir(path):
                try:
                    plugin = Plugin(path)
                    plugin.load_manifest()
                    plugin.load_module()
                    plugin.register(self.engine)
                    self.plugins.append(plugin)
                    print(f"[PluginManager] Loaded plugin {plugin.manifest['name']}")
                except Exception as e:
                    print(f"[PluginManager] Failed to load plugin {item}: {e}")