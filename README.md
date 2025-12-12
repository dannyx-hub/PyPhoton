<div align="center">

# PyPulsar

[![PyPI](https://img.shields.io/pypi/v/PyPulsar.svg)](https://pypi.org/project/PyPulsar/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/PyPulsar.svg)](https://pypi.org/project/PyPulsar/)
[![Stars](https://img.shields.io/github/stars/dannyx-hub/PyPulsar.svg)](https://github.com/dannyx-hub/PyPulsar/stargazers)

**Modern Python desktop framework** – fast, light, secure. Build native apps with HTML/CSS/JS frontend and Python backend. No Electron bloat, no Rust learning curve.

- 🚀 **Lightning Fast**: ~5-15 MB bundles, <100 MB RAM
- 🔒 **Secure by Default**: Built-in ACL (Access Control List) for events
- 🛠️ **Easy CLI**: `pypulsar create my-app && pypulsar dev`
- 🎨 **Native Feel**: WebView on macOS (Cocoa), Windows (Edge), Linux (GTK)

</div>

## Why PyPulsar?

Tired of Electron's 200+ MB RAM? Learning Rust for Tauri? PyPulsar is **Python-first** – leverage your existing skills with NumPy, Pandas, ML models, while getting desktop apps that feel native.

- **Zero Dependencies Overhead**: pywebview + aiohttp = minimal footprint
- **Hot Reload**: Edit HTML/CSS/JS, see changes instantly
- **Plugins System**: Extend with JSON manifests (tray, notifications, updater)
- **Cross-Platform**: Windows, macOS, Linux – one codebase

### Quick Comparison

| Feature          | PyPulsar      | Electron      | Tauri         |
|------------------|---------------|---------------|---------------|
| **Backend Lang** | Python        | Node.js       | Rust          |
| **Bundle Size**  | 5-15 MB       | 100-300 MB    | 0.6-3 MB      |
| **RAM Usage**    | 50-100 MB     | 200+ MB       | <80 MB        |
| **Security**     | ACL + Payload Validation | CSP (manual) | Dynamic ACL   |
| **Mobile**       | No (desktop only) | Partial     | Yes           |
| **Learning Curve** | Low (Python) | Low (JS)     | Medium (Rust) |
| **CLI**          | `pypulsar create` | `electron-forge` | `create-tauri-app` |

PyPulsar shines for Python devs – build tools, dashboards, ML apps without leaving your comfort zone.

## Installation

```bash
pip install PyPulsar
