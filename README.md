# Web Backend Security Simulation and Defense System

Course: Computer Security / Information Security  
Architecture: Node.js (Express), SQLite (better-sqlite3), Vanilla Web Frontend  
Team Scope: SQL Injection, Cross-Site Scripting (XSS), Security Logging and Audit Trail  

---

## 1. System Overview

This application demonstrates common web backend vulnerabilities alongside their respective production-grade mitigations. It features a runtime security toggle allowing side-by-side comparison between Vulnerable Mode and Secure Mode.

* Database: File-based SQLite (`security_demo.db`). Fully self-contained with zero external configuration required on both Linux and Windows environments.
* Vulnerable Mode: Demonstrates raw SQL string interpolation, unescaped DOM/HTML reflections, and missing security headers.
* Secure Mode: Implements parameterized queries, contextual HTML output encoding, strict Content Security Policy (CSP), and HttpOnly cookie flags.
* Security Telemetry: Automated heuristic detection engine classifying incident severity (CRITICAL, HIGH, MEDIUM, LOW) and logging audit trails to SQLite and `logs/security.log`.

---

## 2. Installation and Running

### Prerequisites
* Node.js (version 18 or later)
* npm

### Setup
```bash
npm install
```

### Start Server
```bash
npm start
```
Access the application interface at `http://localhost:3000`.

### Run Automated Attack Verification
```bash
npm run test:attacks
```

---

## 3. Vulnerability Scenarios and Defenses

### SQL Injection (SQLi)
* Authentication Bypass:
  * Vulnerable implementation concatenates user credentials directly into `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`.
  * Attack payload: `admin' --` truncates the password verification predicate.
  * Mitigation: Parameterized prepared statements (`db.prepare('SELECT * FROM users WHERE username = ?')`) and bcrypt password hashing.
* UNION-Based Data Exfiltration:
  * Product search endpoint concatenates search terms into `LIKE '%${query}%'`.
  * Attack payload: `' UNION SELECT id, username, password, 0, role FROM users --`
  * Mitigation: Strict parameter binding for search queries.

### Cross-Site Scripting (XSS)
* Stored XSS:
  * Unsanitized comment submissions are stored in the database and rendered without contextual encoding.
  * Attack payload: `<img src=x onerror=alert('XSS_Stored')>`
  * Mitigation: Server-side HTML entity encoding (`&`, `<`, `>`, `"`, `'`).
* Reflected XSS:
  * Query parameters echoed back in response banners.
  * Mitigation: Output encoding and Content Security Policy enforcement.
* Cookie Hijacking Mitigation:
  * Session cookies are configured with `HttpOnly: true` and `SameSite: Strict`, preventing client-side script access to session tokens.

### Logging and Monitoring
* Tracks attack vectors including SQLi patterns and XSS injection attempts.
* Records source IP, target endpoint, payload data, timestamp, and enforcement action (EXPLOITED vs BLOCKED).
* Provides a real-time administrative audit dashboard at `/api/logs`.
