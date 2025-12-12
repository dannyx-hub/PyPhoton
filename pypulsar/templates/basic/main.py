from pypulsar.engine import Engine
engine = Engine(serve=True, webroot="web", debug=False)
engine.create_window("/index.html", "Photon APP", 1000, 900)
engine.run()
