<div align="center">
# PyPulsar
[![PyPI](https://img.shields.io/pypi/v/PyPulsar.svg)](https://pypi.org/project/PyPulsar/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/PyPulsar.svg)](https://pypi.org/project/PyPulsar/)
[![Stars](https://img.shields.io/github/stars/dannyx-hub/PyPulsar.svg)](https://github.com/dannyx-hub/PyPulsar/stargazers)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pypulsar?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/pypulsar)

**Modern Python desktop framework** – fast, light, secure.  
Build native-feeling desktop apps with HTML/CSS/JS frontend and full Python backend. No Electron bloat, no Rust required.

- 🚀 **Lightning Fast**: ~5–15 MB bundles, <100 MB RAM
- 🔒 **Secure by Default**: Built-in ACL (Access Control List)
- 🛠️ **Easy CLI**: `pypulsar create my-app && pypulsar dev`
- 🎨 **Native WebView**: Cocoa (macOS), Edge (Windows), GTK (Linux)
</div>

## Why PyPulsar?

Tired of Electron's massive RAM usage? Not interested in learning Rust for Tauri?  
PyPulsar is **Python-first** – leverage NumPy, Pandas, ML models, and all your favorite Python libraries while building rich desktop apps with modern web technologies.

- Minimal dependencies (pywebview + aiohttp)
- Hot reload for HTML/CSS/JS during development
- Plugin system (system tray, notifications, auto-updates, etc.)
- Full cross-platform support (Windows, macOS, Linux)

Note: Basic internal plugins are supported today; external plugin distribution via CLI is under development.
### Quick Comparison

| Feature          | PyPulsar             | Electron      | Tauri         |
|------------------|----------------------|---------------|---------------|
| **Backend**      | Python               | Node.js       | Rust          |
| **UI**           | HTML/CSS/JS          | HTML/CSS/JS   | HTML/CSS/JS   |
| **Bundle Size**  | 5–15 MB              | 100–300 MB    | 0.6–3 MB     |
| **RAM Usage**    | 50–100 MB            | 200+ MB       | <80 MB        |
| **Security**     | ACL + validation     | CSP (manual) | Dynamic ACL|
| **Mobile**       | No(Work in progress) | Partial       | Yes           |
| **Learning Curve**| Low (Python + web)   | Low (JS)  | Medium (Rust)| 

Perfect for data dashboards, internal tools, ML interfaces, and utilities.

## Installation

```bash
pip install PyPulsar
```

## Getting Started
Use the CLI to create a new project:
```Bash
pypulsar create my-app --template basic
cd my-app
pypulsar dev  # Development with hot reload
pypulsar build  # For production bundles
```
This generates: main.py (entry point), web/index.html (frontend).

Tip: Run pypulsar --help for more CLI options.

## Basic Example
PyPulsar uses the Engine class to manage the app, serve static files, and create windows.
```python
from pypulsar.engine import Engine

engine = Engine(serve=True, webroot="web", debug=True)
engine.create_window("/index.html", "PyPulsar App", 900, 700)
engine.run()
```
Frontend files go in the web/ folder (e.g., web/index.html).
web/index.html example:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PyPulsar App</title>
</head>
<body>
    <h1>Hello from PyPulsar!</h1>
    <p>This is a full HTML/CSS/JS frontend with live DOM manipulation.</p>
</body>
</html>
```
- Live DOM manipulation: Full and direct in JavaScript – just like a regular web app.
- Python → JS: Use `engine.window.evaluate_js("your JS code")` to push updates (e.g., background tasks, ML results).
- JS → Python: Expose Python functions via pywebview's js_api (enhanced with ACL for security).

## Simple Counter with Bidirectional Communication and ACL
```python
from pypulsar.engine import Engine, Hooks
from pypulsar.acl import acl

# Allow the event in ACL
acl.allow("increment_counter")

engine = Engine(serve=True, webroot="web", debug=False)

counter = 0

def handle_event(event_name, data):
    global counter
    if event_name == "increment_counter":
        counter += 1
        window.evaluate_js(
            f"document.getElementById('counter').innerText = '{counter}';"
        )

engine.register_hook(Hooks.ON_EVENT, handle_event)

window = engine.create_window(
    path="/index.html",
    title="Counter App",
    width=800,
    height=600
)
engine.run()
```
**web/index.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Counter App</title>
</head>
<body>
    <h1>Counter: <span id="counter">0</span></h1>
    <button onclick="increment()">Increment</button>
    <script>
        function increment() {
            // Send event to Python (validated by ACL)
            window.pywebview.api.pywebview_message('increment_counter', {});
        }
    </script>
</body>
</html>
```
Note: Avoid calling evaluate_js before engine.run(). Use window.events.loaded for initial UI setup.


## Security: Built-in ACL
PyPulsar's ACL is default-deny: JS events are blocked unless whitelisted.
```python
from pypulsar.acl import acl

acl.allow("event_name")  # Simple whitelist

# Optional validator
@acl.validator("event_name")
def validate_payload(payload):
    return 'key' in payload and payload['key'] == 'secret'  # Return bool
```
- Deny with acl.deny("pattern").
- Protects against unauthorized frontend access.



## Project Status
PyPulsar is currently in beta.

The framework is under active development and new features, APIs, and improvements are delivered on a regular basis.
Breaking changes may occur as the architecture is refined, so early adopters should expect some evolution in interfaces and behavior.

Despite the beta status, the core concepts (plugin system, backend–frontend bridge,
application lifecycle) are already usable and stable enough for experimentation, prototypes, and internal tools.

## Mobile Support (Work in progress)
Support for mobile platforms is actively being explored.

At the moment, development is focused on Android as the first supported mobile target.
The goal is to enable PyPulsar applications to run using the same core architecture, plugin system, and API surface across desktop and mobile environments.

Mobile support is still work in progress and not yet considered production-ready. 
Updates related to Android integration will be introduced incrementally as the framework evolves.

## Plugin Ecosystem (Work in progress)
Work is currently underway on expanding the plugin ecosystem and improving plugin distribution.

One of the key goals is to introduce first-class CLI support for plugins, allowing developers to:
- easily install external plugins via the PyPulsar CLI,
- manage plugin versions (install, update, downgrade),
- enable or disable plugins per application,
- ensure compatibility between the framework version and installed plugins.

This will make PyPulsar’s plugin system more modular, discoverable, and suitable for building reusable extensions maintained independently from the core framework.

The plugin manager and CLI workflow are still under active development and will be introduced incrementally in upcoming releases.
