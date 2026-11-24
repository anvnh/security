# AGENTS.md

## Project Overview

Build a minimal web application to demonstrate common web security
vulnerabilities and their corresponding countermeasures:

- SQL Injection (SQLi) — Full Attack Chain: Data Exfiltration via Search & Authentication Bypass via Login
- Stored Cross-Site Scripting (XSS)

The application must resemble a normal website rather than a cybersecurity
dashboard. Security demonstrations should be integrated into realistic features.

## Technology Stack

- Language: Python 3.13
- Backend: Flask
- Frontend: HTML, CSS, Vanilla JavaScript, Jinja2
- Database: SQLite with Python's built-in sqlite3
- Password Hashing: Argon2id
- Testing: Pytest
- Version Control: Git and GitHub

Do not introduce additional frameworks, databases, or dependencies unless
strictly necessary.

## Application Features

Build a minimal blog-style application with:

- User registration and login (SQLi Authentication Bypass target)
- User logout
- Post listing and searching (SQLi Data Exfiltration target)
- Post comments (Stored XSS target)

Each feature should serve a practical security demonstration purpose.
Avoid unrelated features.

## Security Mode

Provide two security modes within the same application:

| Vulnerability | Vulnerable Mode | Secure Mode |
| --- | --- | --- |
| SQL Injection | Unsafe query construction in search & login | Parameterized queries + Argon2id verification |
| XSS | Unescaped user-controlled content | Context-aware output encoding |

Requirements:

- Provide a small floating security toggle on every main application page,
  similar to a light/dark mode switch.
- Clearly indicate whether security is enabled or disabled.
- Default to Secure Mode.
- Manage security mode on the backend using session-scoped state.
- Preserve the selected mode across authentication transitions.
- Switching modes must not require restarting the application.
- Both modes must use the same interface and application features.
- Only disable countermeasures explicitly required for demonstrations.
- Keep the security toggle endpoint protected in both modes.
- Keep password hashing enabled in both modes.

## Demonstration Guide

Provide a dedicated route at `/lab/guide`.

This route must be separate from the normal application navigation and
serve as a reference page for presenters.

Include the following for each vulnerability:

- Vulnerability description and root cause
- Target page or feature
- Demonstration prerequisites
- Reproducible local test steps and copyable test inputs
- Expected behavior in Vulnerable Mode
- Expected behavior in Secure Mode
- Implemented countermeasures
- Relevant source code references

Include copy buttons for demonstration inputs and a reliable way to reset
the laboratory to its initial state.

## UI and Design

- Use a minimal, GitHub-inspired dark color scheme.
- Use a consistent dark background and subtle borders.
- Use system fonts and simple, readable typography.
- Keep layouts clean, responsive, and accessible.
- Avoid gradients, excessive animations, and decorative elements.
- Do not use frontend frameworks or external UI libraries.
- Keep the security toggle small but clearly visible.
- Keep the main website visually independent of the demonstration guide.

## Development Environment

The project must support both Linux and Windows natively.

- Use Python virtual environments (`.venv`).
- Pin dependencies in `requirements.txt`.
- Use `pathlib` for filesystem paths.
- Do not require Bash, WSL, Docker, or platform-specific tools.
- Provide documented setup instructions for Linux and Windows.
- Provide a cross-platform database initialization and reset command.
- Do not commit virtual environments, databases, secrets, or generated files.

## Coding Standards

- Write all code, comments, documentation, and commit messages in English.
- Follow PEP 8 and use four-space indentation.
- Use descriptive variable and function names.
- Separate routes, database operations, and security logic.
- Centralize security mode management.
- Avoid unnecessary abstractions and duplicated logic.
- Prefer simplicity, readability, and maintainability.

## Git Workflow

- Keep `main` stable and runnable.
- Create a separate feature branch for each task.
- Use Conventional Commits.
- Submit changes through pull requests.
- Keep commits small and focused.
- Do not modify unrelated files.

## Testing

- Test every vulnerability in both security modes.
- Verify that enabling security prevents the demonstrated attack.
- Verify that legitimate application behavior works in both modes.
- Test security mode isolation between sessions.
- Verify that database reset restores predictable demonstration data.
- Run all tests before merging changes.

## Laboratory Safety

- Treat this application as an educational security laboratory.
- Bind the application to localhost by default.
- Use synthetic accounts and demonstration data only.
- Never expose Vulnerable Mode to the public Internet.
- Do not target external systems during demonstrations.
- Keep intentionally vulnerable behavior isolated and clearly documented.

## Definition of Done

A feature is complete when:

- It works on both Linux and Windows.
- Its vulnerable and secure behaviors are reproducible.
- Its security countermeasures are implemented and tested.
- Its demonstration instructions are documented in `/lab/guide`.
- It follows the existing architecture and visual design.

## Core Principle

Build the simplest application that clearly demonstrates the vulnerability,
its root cause, and the effectiveness of its countermeasures.

Security demonstration quality takes priority over application complexity.
