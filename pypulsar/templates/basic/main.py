from pypulsar.engine.desktop_engine import DesktopEngine
engine = DesktopEngine(serve=True, webroot="web", debug=False)
engine.create_window("/index.html", "Photon APP", 1000, 900)
engine.run()
