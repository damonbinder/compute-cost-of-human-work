#!/usr/bin/env python3
"""Decrypt one HAL trace zip from agent-evals/hal_traces into a JSON file.

HAL encrypts every uploaded run with a fixed password, published in its own
harness at hal/utils/decrypt.py (``JsonEncryption("hal1234", salt=salt_bytes)``).
Each zip member is a JSON envelope {"encrypted_data": b64, "salt": b64};
the key is PBKDF2-HMAC-SHA256(password, salt, 480000 iterations), Fernet.

Dependencies: cryptography.

Usage:
    python3 decrypt_hal_zip.py <input.zip> <output.json>
"""
import base64
import json
import sys
import zipfile

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSWORD = b"hal1234"


def decrypt_zip(zip_path, out_path):
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if len(names) != 1:
            raise SystemExit(f"expected 1 member, got {names}")
        env = json.load(zf.open(names[0]))
    salt = base64.b64decode(env["salt"])
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    key = base64.urlsafe_b64encode(kdf.derive(PASSWORD))
    plain = Fernet(key).decrypt(base64.b64decode(env["encrypted_data"]))
    with open(out_path, "wb") as fh:
        fh.write(plain)
    return len(plain)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    n = decrypt_zip(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]} ({n} bytes)")
