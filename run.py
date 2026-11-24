"""Application entry point running the pure user blog (:5000) and lab/attacker server (:5001)."""

import threading
from werkzeug.serving import make_server
from app import create_app
from app.db import init_db
from app.config import DATABASE_PATH, Config

blog_app = create_app(role="blog")
lab_app = create_app(role="lab")
# Default app exported for Flask CLI commands (init-db / reset-db)
app = blog_app


def _serve(flask_app, host: str, port: int):
    """Serve a Flask WSGI app on the specified host and port."""
    server = make_server(host, port, flask_app, threaded=True)
    server.serve_forever()


if __name__ == "__main__":
    if not DATABASE_PATH.exists():
        init_db(DATABASE_PATH)

    host = "127.0.0.1"
    blog_port = Config.BLOG_PORT
    lab_port = Config.LAB_PORT

    blog_app.debug = True
    lab_app.debug = True

    print(f" * User Blog running on       http://{host}:{blog_port}/")
    print(f" * Lab Guide running on       http://{host}:{lab_port}/lab/guide")
    print(f" * Attacker C2 running on     http://{host}:{lab_port}/lab/attacker")

    lab_thread = threading.Thread(
        target=_serve,
        args=(lab_app, host, lab_port),
        daemon=True,
    )
    lab_thread.start()

    try:
        # Bind to localhost by default for laboratory safety
        _serve(blog_app, host, blog_port)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
