"""Application entry point for running the security laboratory."""

from app import create_app
from app.db import init_db
from app.config import DATABASE_PATH

app = create_app()

if __name__ == "__main__":
    if not DATABASE_PATH.exists():
        init_db(DATABASE_PATH)
    # Bind to localhost by default for laboratory safety
    app.run(host="127.0.0.1", port=5000, debug=True)
