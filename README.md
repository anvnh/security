# Web Security Demonstration Laboratory

A minimal blog-style web application built to demonstrate common web security vulnerabilities and their production-grade countermeasures:

- **SQL Injection (SQLi) — Full Attack Chain**:
  - Phase 1: Data Exfiltration via Search (`/?q=`)
  - Phase 2: Authentication Bypass via Login (`/login`)
- **Stored Cross-Site Scripting (XSS)**: Unescaped user-controlled content vs Context-aware output encoding

---

## Technology Stack

- **Language**: Python 3.13+
- **Backend Framework**: Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Jinja2
- **Database**: SQLite (Python's built-in `sqlite3`)
- **Password Hashing**: Argon2id (`argon2-cffi`)
- **Testing**: Pytest

---

## Architecture Overview

```
security/
├── app/
│   ├── __init__.py          # Flask application factory (create_app)
│   ├── config.py            # App configuration with pathlib support
│   ├── security.py          # Centralized security mode management & Argon2id
│   ├── db.py                # Database connection, init, reset, and CLI commands
│   ├── schema.sql           # Database schema definition
│   ├── seed.sql             # Predictable demonstration seed data (8 users)
│   ├── routes/
│   │   ├── auth.py          # Register, login (SQLi Auth Bypass target), logout
│   │   ├── blog.py          # Post list, search (SQLi Data Exfiltration target), comments (XSS target)
│   │   ├── security_mode.py # Security mode toggle endpoint
│   │   └── lab.py           # Demonstration guide (/lab/guide) and reset endpoint
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css    # Minimal GitHub-dark inspired theme
│   │   │   └── lab.css      # Lab guide specific styling
│   │   └── js/
│   │       ├── main.js      # Vanilla JS for toggle
│   │       └── lab.js       # Copy-to-clipboard functionality
│   └── templates/
│       ├── base.html        # Base layout with floating security toggle
│       ├── auth/            # Sign in and registration templates
│       ├── blog/            # Feed, search, and post detail templates
│       └── lab/
│           └── guide.html   # Presenter demonstration guide
├── tests/                   # Pytest test suite (100% vulnerability coverage)
├── requirements.txt         # Pinned production dependencies
├── run.py                   # Application launch script (binds to 127.0.0.1)
├── init_db.py               # Cross-platform database initialization and reset script
└── README.md                # Project documentation and setup instructions
```

---

## Setup Instructions

### Prerequisites
- Python 3.13 or newer installed.
- Git.

### Linux Setup
```bash
# 1. Clone repository (if not already done)
git clone https://github.com/anvnh/security.git
cd security

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install pinned dependencies
pip install -r requirements.txt

# 5. Initialize database
python init_db.py init

# 6. Run the application
python run.py
```

### Windows Setup (Command Prompt or PowerShell)
```cmd
:: 1. Navigate to directory
cd security

:: 2. Create virtual environment
python -m venv .venv

:: 3. Activate virtual environment
:: Command Prompt:
.venv\Scripts\activate.bat
:: Or PowerShell:
.venv\Scripts\Activate.ps1

:: 4. Install pinned dependencies
pip install -r requirements.txt

:: 5. Initialize database
python init_db.py init

:: 6. Run the application
python run.py
```

The application runs two local servers simultaneously:
- **User Blog (`http://127.0.0.1:5000/`)**: Clean user-facing blog without lab controls or security toggle UI.
- **Lab Guide (`http://127.0.0.1:5001/lab/guide`)**: Presenter demonstration guide with the global security mode toggle and lab reset control.
- **Attacker C2 Panel (`http://127.0.0.1:5001/lab/attacker`)**: Simulated credential harvesting listener (cannot toggle security mode).

---

## Security Mode Toggle

The security mode toggle is exclusively available on the presenter guide (`http://127.0.0.1:5001/lab/guide`):
- **Default State**: **Secure Mode** (`ON`).
- **Toggle**: Switch between **Secure Mode** and **Vulnerable Mode** without restarting the servers.
- **Global SQLite State**: Mode is stored in SQLite (`lab_settings`) so changes made on `:5001/lab/guide` immediately apply across all clients visiting `:5000`.
- **Isolated Controls**: Neither `:5000` (User Blog) nor `:5001/lab/attacker` exposes the security toggle.
- **Password Hashing**: Argon2id password hashing remains active in both modes.

---

## Demonstration Guide (`http://127.0.0.1:5001/lab/guide`)

Visit `http://127.0.0.1:5001/lab/guide` for full presenter instructions, copyable payloads, and expected outputs.

### Pre-seeded Accounts
| Username | Password | Role |
| --- | --- | --- |
| `admin` | `admin123` | System Administrator |
| `alice` | `alice123` | Security Analyst |
| `bob` | `bob123` | Software Engineer |
| `john` | `H3FDWr_WgR7p6LVC` | Distributed Systems Developer |
| `sarah` | `iUXPrZ00FLZCfVzI` | Frontend Developer |
| `david` | `KFwzi5tZyl1RsYu0` | DevOps Engineer |
| `emily` | `IAcRKMR-D-FKtyyJ` | Data Scientist |
| `alex` | `BhGAFzQZOXKF39Ch` | CS Student |

### Database Reset
To restore all demonstration data to its pristine initial state, click **"Reset Laboratory State"** on `/lab/guide` or run:
```bash
python init_db.py reset
```
or via Flask CLI:
```bash
flask --app run:app reset-db
```

---

## Running the Test Suite

Run pytest to verify vulnerabilities and defenses across both security modes:

```bash
pytest
```
