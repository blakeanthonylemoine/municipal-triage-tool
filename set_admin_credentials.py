# set_admin_credentials.py
"""Interactively sets (or resets) the single global admin login.

Run this yourself: `uv run python set_admin_credentials.py`
Prompts for an email and a hidden password, hashes the password, and
writes ADMIN_EMAIL / ADMIN_PASSWORD_HASH into .env (replacing any
existing values for those two keys, leaving everything else alone).
"""
import getpass
from pathlib import Path

from auth import hash_password

ENV_PATH = Path(__file__).parent / ".env"


def upsert_env_var(lines: list[str], key: str, value: str) -> list[str]:
    prefix = f"{key}="
    new_line = f'{key}="{value}"'
    for i, line in enumerate(lines):
        if line.strip().startswith(prefix):
            lines[i] = new_line
            return lines
    lines.append(new_line)
    return lines


def main():
    email = input("Admin email: ").strip()
    password = getpass.getpass("Admin password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords did not match. Nothing was changed.")
        return
    if not email or not password:
        print("Email and password are both required. Nothing was changed.")
        return

    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    lines = upsert_env_var(lines, "ADMIN_EMAIL", email)
    lines = upsert_env_var(lines, "ADMIN_PASSWORD_HASH", hash_password(password))
    ENV_PATH.write_text("\n".join(lines) + "\n")

    print(f"Admin credentials set for {email}. Restart the backend for this to take effect.")


if __name__ == "__main__":
    main()
