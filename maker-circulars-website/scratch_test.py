"""
Reconcile Everllence Service Letters with Maker Circulars Database
Dry-run test script to verify all records, links, and transactions before committing.
"""

import os
import sys
import json
import time
import secrets
import sqlite3
import datetime
import urllib.request
import urllib.parse
import ssl
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "data", "maker_circulars.db")
SOURCE_URL = "https://www.everllence.com/services/offerings/marine-power/service-letters"
ARCHIVE_URL = "https://www.man-es.com/services/industries/marine/service-letters"

print(f"Database Path: {DB_PATH}")
print(f"Source URL:    {SOURCE_URL}")
print(f"Archive URL:   {ARCHIVE_URL}")

def generate_object_id():
    """Generate a 24-character hex MongoDB-compatible ObjectId."""
    # 4 bytes timestamp (big endian) + 5 bytes random + 3 bytes counter
    t = int(time.time())
    timestamp_hex = f"{t:08x}"
    rest_hex = secrets.token_hex(8)
    return timestamp_hex + rest_hex

# Test generation
sample_id = generate_object_id()
print(f"Sample generated _id: {sample_id} (len: {len(sample_id)})")
