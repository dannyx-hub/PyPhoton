## PyPhoton

### 🌟 Project Description

PyPhoton is a lightweight “Electron-like” Python framework for building modern desktop applications using web technologies (HTML/CSS/JS) while fully integrating with Python.

It is designed for simplicity and performance, and future versions will support a plugin system, enabling dynamic extension of functionality and customization.


### ⚡ Features

- Runs a local HTTP server for web assets.
- Creates desktop windows with embedded web pages.
- Bi-directional communication between Python and JavaScript.
- Debug mode for easier development.
- Coming soon: plugin system for dynamic feature extensions.

### 🛠 Installation
```bash
git clone https://github.com/YOUR_USERNAME/PyPhoton.git
cd PyPhoton
pip install -r requirements.txt
```

### 🚀 Example Usage
```python
from pyphoton import Engine

engine = Engine(debug=True)
engine.create_window(path="/index.html", title="My Application")
engine.run()

```
### 🔌 Plugin System (Coming Soon)

PyPhoton will support a robust plugin architecture, allowing developers to:
- Easily add new features to applications.
- Extend Python ↔ JavaScript communication.
- Dynamically load and unload plugins at runtime.
- Safely isolate plugins to prevent crashes or security issues.
- Plugin manifests will define plugin name, version, entry points, and hooks for seamless integration with PyPhoton.

#### Example Plugin Structure
```
plugins/
    my_plugin/
        __init__.py
        plugin.json
        main.py
        assets/

```
##### plugin.json example
```json
{
  "name": "MyPlugin",
  "version": "1.0.0",
  "entry": "main.py",
  "hooks": ["on_window_create", "on_event"],
  "min_engine_version": "1.0.0"
}

```
#### 🛡 Safety & Isolation

- Plugins run in a sandboxed environment or isolated thread/process.
- Only a restricted API is exposed to plugins.
- Engine validates plugin manifests, versions, and compatibility before loading.
- Plugin errors are logged centrally and do not crash the main application.