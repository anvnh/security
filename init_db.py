"""Cross-platform script for database initialization and reset."""

import sys
from app.db import reset_db
from app.config import DATABASE_PATH

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "init"
    if action in ("init", "reset"):
        reset_db(DATABASE_PATH)
        print(f"Database successfully {action}ed at {DATABASE_PATH}")
    else:
        print(f"Usage: python init_db.py [init|reset]")
        sys.exit(1)
