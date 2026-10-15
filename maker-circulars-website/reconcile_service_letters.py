"""
Reconcile Everllence Service Letters with Maker Circulars Database
Integrates with the existing application architecture, database, models, and schema.

Usage:
    python reconcile_service_letters.py [--dry-run]
"""

import os
import sys
import json
import time
import shutil
import secrets
import sqlite3
import datetime
import html
import re
import urllib.request
import urllib.parse
import ssl

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "maker_circulars.db")
AUDIT_FILE = os.path.join(DATA_DIR, "everllence_source_audit.json")

EVERLLENCE_SOURCE_URL = "https://www.everllence.com/services/offerings/marine-power/service-letters"
MAN_ES_ARCHIVE_URL = "https://www.man-es.com/services/industries/marine/service-letters"

# Browser-like headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def create_backup() -> str:
    """Create a timestamped backup of the database before modifying anything."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"maker_circulars_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def generate_unique_object_id(existing_ids: set) -> str:
    """Generate a unique 24-character hex ID (MongoDB ObjectId format)."""
    while True:
        # 4 bytes timestamp (8 hex chars) + 8 bytes random (16 hex chars) = 24 hex chars
        t = int(time.time())
        obj_id = f"{t:08x}" + secrets.token_hex(8)
        if obj_id not in existing_ids:
            existing_ids.add(obj_id)
            return obj_id


def fetch_page_content(url: str) -> str:
    """Fetch HTML content from a URL."""
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_everllence_documents(html_content: str) -> list:
    """
    Extract all download entries from div.download-list containers on the Everllence page.
    Locates each div.download-meta, extracts document-title text, and extracts the URL from
    the corresponding div.download-button link element.
    """
    pattern = re.compile(
        r'<div class="download-item">.*?<div class="download-meta">\s*<h5 class="document-title">\s*(.*?)\s*</h5>.*?<div class="download-button">\s*<a\s+[^>]*href="([^"]+)".*?</div>\s*</div>',
        re.DOTALL
    )

    items = []
    for raw_title, href in pattern.findall(html_content):
        clean_title = html.unescape(raw_title)
        clean_title = re.sub(r"\s+", " ", clean_title).strip()

        full_url = urllib.parse.urljoin(EVERLLENCE_SOURCE_URL, href.strip())

        # Extract publication identifier like SL2026-790 if present
        sl_match = re.search(r"(SL\d{4}-\d{3})", clean_title, re.IGNORECASE)
        pub_id = sl_match.group(1).upper() if sl_match else None

        is_toc = "table of content" in clean_title.lower()

        items.append({
            "source": "Everllence",
            "source_page": EVERLLENCE_SOURCE_URL,
            "title": clean_title,
            "download_url": full_url,
            "pub_id": pub_id,
            "is_toc": is_toc
        })

    return items


def extract_archive_service_letters(html_content: str) -> list:
    """Extract service letters from the older MAN-ES archive page for reference."""
    li_blocks = re.findall(r'<li class="list__item[^"]*">(.*?)</li>', html_content, re.DOTALL)
    items = []
    for li in li_blocks:
        title_match = re.search(r'class="listItem__title">\s*(.*?)\s*</span>', li, re.DOTALL)
        desc_matches = re.findall(r'class="listItem__description">\s*(.*?)\s*</div>', li, re.DOTALL)
        href_match = re.search(r'class="listItem__downloadText"[^>]*href="([^"]+)"', li)

        if title_match and href_match:
            t = html.unescape(re.sub(r'<[^>]+>', '', title_match.group(1))).strip()
            d = ""
            for dm in desc_matches:
                cleaned = html.unescape(re.sub(r'<[^>]+>', '', dm)).strip()
                if not cleaned.lower().startswith('pdf') and len(cleaned) > 0:
                    d = cleaned
                    break

            full_title = f"{t} {d}".strip() if d else t
            if "table of content" in full_title.lower():
                continue

            full_url = urllib.parse.urljoin(MAN_ES_ARCHIVE_URL, href_match.group(1).strip())
            sl_match = re.search(r"(SL\d{4}-\d{3})", t, re.IGNORECASE)
            pub_id = sl_match.group(1).upper() if sl_match else None

            items.append({
                "source": "MAN-ES Archive",
                "source_page": MAN_ES_ARCHIVE_URL,
                "title": full_title,
                "download_url": full_url,
                "pub_id": pub_id,
                "is_toc": False
            })

    return items


def verify_pdf_link(url: str) -> tuple[bool, str, int]:
    """
    Verify that the URL points to an accessible HTTP/HTTPS PDF document.
    Returns (is_valid, final_url, size_bytes).
    """
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, url, 0

    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status != 200:
                return False, resp.geturl(), 0

            final_url = resp.geturl()
            content_type = resp.headers.get("Content-Type", "")
            content_length = int(resp.headers.get("Content-Length", 0))

            # Inspect first 1024 bytes for PDF header
            chunk = resp.read(1024)
            if b"%PDF" in chunk or "pdf" in content_type.lower():
                return True, final_url, (content_length or len(chunk))
            return False, final_url, 0
    except Exception as e:
        print(f"  [VERIFY ERROR] {url}: {e}")
        return False, url, 0


def normalize_title(t: str) -> str:
    """Normalize title for comparison: lowercase, punctuation removed, collapsed whitespace."""
    t = html.unescape(t).lower()
    t = re.sub(r"[^\w\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def reconcile(dry_run: bool = False) -> dict:
    print("=" * 75)
    print("  EVERLLENCE MAN B&W SERVICE LETTERS SYNCHRONIZATION")
    print(f"  Mode: {'DRY RUN (Audit only, no database writes)' if dry_run else 'LIVE UPDATE'}")
    print("=" * 75)

    # 1. Inspect existing database
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Active dataset
    dataset_row = cur.execute(
        "SELECT id, row_count, column_names FROM datasets WHERE status = 'active' LIMIT 1"
    ).fetchone()
    if not dataset_row:
        raise ValueError("No active dataset found in database!")
    dataset_id, current_row_count, column_names_json = dataset_row
    print(f"\n[DATABASE] Target Dataset ID: {dataset_id}")
    print(f"[DATABASE] Current Dataset Row Count: {current_row_count}")

    # Inspect MAN B&W Maker records
    man_bw_maker = "MAN B&W"
    existing_rows = cur.execute(
        "SELECT id, data FROM records WHERE dataset_id = ? AND json_extract(data, '$.maker') = ?",
        (dataset_id, man_bw_maker)
    ).fetchall()
    print(f"[DATABASE] Found {len(existing_rows)} existing records for Maker '{man_bw_maker}'")

    existing_docs = []
    all_existing_ids = set()
    for rid, d_str in cur.execute("SELECT id, json_extract(data, '$._id') FROM records").fetchall():
        if d_str:
            all_existing_ids.add(d_str)

    for rid, d_str in existing_rows:
        data = json.loads(d_str)
        doc_name = data.get("document_name", "")
        existing_docs.append({
            "id": rid,
            "_id": data.get("_id"),
            "document_name": doc_name,
            "document_link": data.get("document_link", ""),
            "breadcrumb": data.get("breadcrumb", ""),
            "dms": data.get("dms", True),
            "normalized": normalize_title(doc_name)
        })

    # 2. Extract documents from Everllence live page
    print(f"\n[SOURCE] Fetching official Everllence page: {EVERLLENCE_SOURCE_URL} ...")
    everllence_html = fetch_page_content(EVERLLENCE_SOURCE_URL)
    extracted_docs = extract_everllence_documents(everllence_html)
    print(f"[SOURCE] Extracted {len(extracted_docs)} total documents from Everllence download lists")

    # Save audit file
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_docs, f, indent=2)
    print(f"[AUDIT] Saved extracted source audit data to: {AUDIT_FILE}")

    # Optional inspection of older archive
    archive_docs = []
    try:
        archive_html = fetch_page_content(MAN_ES_ARCHIVE_URL)
        archive_docs = extract_archive_service_letters(archive_html)
        print(f"[SOURCE] Extracted {len(archive_docs)} reference letters from older MAN ES archive")
    except Exception as e:
        print(f"[SOURCE ARCHIVE WARNING] Could not fetch older archive: {e}")

    # 3. Classify Extracted Documents: Already present, Missing, Needs review
    print("\n" + "=" * 75)
    print("  CLASSIFYING EVERLLENCE DOCUMENTS AGAINST DATABASE")
    print("=" * 75)

    already_present = []
    missing_to_insert = []
    needs_review = []

    for item in extracted_docs:
        title = item["title"]
        pub_id = item["pub_id"]
        is_toc = item["is_toc"]
        norm_title = normalize_title(title)

        # Table of contents documents: Flag for review
        if is_toc:
            # Check if TOC exists in DB
            toc_matches = [
                d for d in existing_docs
                if "table of content" in d["normalized"] or "table-of-content" in d["normalized"]
            ]
            needs_review.append({
                "item": item,
                "reason": "Table of Contents / Index document (not an individual service letter).",
                "potential_matches": [f"ID {m['id']}: {m['document_name']}" for m in toc_matches]
            })
            print(f"[NEEDS REVIEW - TOC] {title}")
            continue

        matched_doc = None
        # Match by Publication ID (e.g. SL2026-790)
        if pub_id:
            for edoc in existing_docs:
                if pub_id in edoc["document_name"].upper():
                    matched_doc = edoc
                    break

        # Match by normalized full title
        if not matched_doc:
            for edoc in existing_docs:
                if edoc["normalized"] == norm_title:
                    matched_doc = edoc
                    break

        if matched_doc:
            already_present.append({
                "source_item": item,
                "db_match": matched_doc
            })
            print(f"[ALREADY PRESENT] {title}")
            print(f"   -> Matched DB Record ID {matched_doc['id']}: '{matched_doc['document_name']}'")
        else:
            missing_to_insert.append(item)
            print(f"[MISSING - TO INSERT] {title}")

    # 4. Verify PDF Links for Missing Documents
    verified_to_insert = []
    verification_failed = []

    if missing_to_insert:
        print("\n" + "=" * 75)
        print("  VERIFYING PDF DOWNLOAD LINKS FOR MISSING DOCUMENTS")
        print("=" * 75)
        for item in missing_to_insert:
            url = item["download_url"]
            print(f"Verifying: {item['title']}")
            print(f"  URL: {url}")
            is_valid, final_url, size = verify_pdf_link(url)
            if is_valid:
                print(f"  [OK] Valid PDF confirmed ({size} bytes, URL: {final_url})")
                item["verified_url"] = final_url
                item["file_size"] = size
                verified_to_insert.append(item)
            else:
                print(f"  [FAILED] Could not verify PDF at {url}")
                verification_failed.append(item)
    else:
        print("\n[INFO] No missing documents to verify or insert. Database is up to date!")

    # 5. Prepare Records for Insertion
    records_to_insert = []
    for item in verified_to_insert:
        year_match = re.search(r"SL(\d{4})", item["title"], re.IGNORECASE)
        year = year_match.group(1) if year_match else datetime.datetime.now().strftime("%Y")
        breadcrumb = f"Maker Circulars > MAN B&W > {year}"

        record_data = {
            "maker": man_bw_maker,
            "breadcrumb": breadcrumb,
            "document_name": item["title"],
            "document_link": item["verified_url"],
            "is_new": True,
            "date_of_upload": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        records_to_insert.append(record_data)

    # 6. Database Update (with transaction & idempotency check)
    backup_file = None
    inserted_count = 0

    if records_to_insert:
        if dry_run:
            print("\n[DRY RUN] Skipping database backup and inserts.")
        else:
            backup_file = create_backup()
            print(f"\n[BACKUP] Created database backup at: {backup_file}")

            try:
                now_iso = datetime.datetime.utcnow().isoformat()
                for r_data in records_to_insert:
                    # Idempotency check immediately before insertion
                    doc_name_check = r_data["document_name"]
                    exists_check = cur.execute(
                        "SELECT id FROM records WHERE dataset_id = ? AND json_extract(data, '$.document_name') = ?",
                        (dataset_id, doc_name_check)
                    ).fetchone()

                    if exists_check:
                        print(f"[SKIP DUPLICATE] Record already exists: {doc_name_check}")
                        continue

                    cur.execute(
                        "INSERT INTO records (dataset_id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (dataset_id, json.dumps(r_data), now_iso, now_iso)
                    )
                    inserted_count += 1

                new_row_count = current_row_count + inserted_count
                cur.execute("UPDATE datasets SET row_count = ? WHERE id = ?", (new_row_count, dataset_id))
                conn.commit()
                print(f"[TRANSACTION] Successfully committed {inserted_count} new records to database.")
                print(f"[TRANSACTION] Updated dataset row_count to {new_row_count}.")
            except Exception as e:
                conn.rollback()
                print(f"[ERROR] Database transaction failed and rolled back: {e}")
                raise e
    else:
        print("\n[TRANSACTION] No new records needed insertion.")

    conn.close()

    # 7. Summary
    print("\n" + "=" * 75)
    print("  SYNCHRONIZATION RESULTS SUMMARY")
    print("=" * 75)
    print(f"Total entries extracted from webpage: {len(extracted_docs)}")
    print(f"Entries already present in database:  {len(already_present)}")
    print(f"New records inserted:                 {inserted_count}")
    print(f"Entries requiring manual review:      {len(needs_review)}")
    print(f"Failed PDF verifications:            {len(verification_failed)}")
    if backup_file:
        print(f"Backup file created:                  {backup_file}")
    print("=" * 75)

    return {
        "total_extracted": len(extracted_docs),
        "already_present_count": len(already_present),
        "already_present": already_present,
        "missing_count": len(missing_to_insert),
        "inserted_count": inserted_count,
        "records_inserted": records_to_insert if not dry_run else [],
        "needs_review_count": len(needs_review),
        "needs_review": needs_review,
        "verification_failed": verification_failed,
        "backup_file": backup_file,
        "audit_file": AUDIT_FILE
    }


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    reconcile(dry_run=is_dry_run)
