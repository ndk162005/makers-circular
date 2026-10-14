import os
import sys
import json
import sqlite3
import httpx
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from reconcile_service_letters import (
    extract_everllence_documents,
    fetch_page_content,
    verify_pdf_link,
    EVERLLENCE_SOURCE_URL,
    reconcile,
    DB_PATH,
    AUDIT_FILE
)

def test_1_extract_live_page():
    print("=== Test 1: Live Page Extraction ===")
    html = fetch_page_content(EVERLLENCE_SOURCE_URL)
    docs = extract_everllence_documents(html)
    assert len(docs) == 24, f"Expected 24 documents, got {len(docs)}"
    
    # Check all have titles and URLs
    for d in docs:
        assert d["title"], "Document title cannot be empty"
        assert d["download_url"].startswith("http"), f"Invalid URL: {d['download_url']}"
        assert "?" in d["download_url"], f"Query parameters should be preserved: {d['download_url']}"
    
    # Check specific newly added SL numbers are present
    titles = [d["title"] for d in docs]
    assert any("SL2026-790" in t for t in titles)
    assert any("SL2026-789" in t for t in titles)
    assert any("SL2026-788" in t for t in titles)
    assert any("SL2026-787" in t for t in titles)
    print("  [PASS] Successfully extracted 24 documents with titles, query params, and valid URLs.")

def test_2_database_integrity_and_fields():
    print("\n=== Test 2: Database Integrity & Fields ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Active dataset
    ds = cur.execute("SELECT id, row_count, column_names FROM datasets WHERE status = 'active'").fetchone()
    assert ds is not None
    assert ds[1] == 1220, f"Expected 1220 total records in dataset, got {ds[1]}"
    col_names = json.loads(ds[2])
    assert "_id" not in col_names and "dms" not in col_names, "Neither _id nor dms should be in datasets.column_names"
    assert "maker" in col_names and "document_name" in col_names
    
    # Check column definitions table
    col_defs = cur.execute("SELECT name FROM column_definitions WHERE dataset_id = ?", (ds[0],)).fetchall()
    col_def_names = [c[0].lower() for c in col_defs]
    assert "_id" not in col_def_names, "_id should be deleted from column_definitions"
    assert "dms" not in col_def_names, "dms should be deleted from column_definitions"
    assert "id" not in col_def_names, "id should be deleted from column_definitions"

    # Check MAN B&W records
    man_bw_rows = cur.execute(
        "SELECT id, data FROM records WHERE dataset_id = ? AND json_extract(data, '$.maker') = 'MAN B&W'",
        (ds[0],)
    ).fetchall()
    assert len(man_bw_rows) == 294, f"Expected 294 MAN B&W records, got {len(man_bw_rows)}"
    
    # Verify no records have _id or dms in data
    records_with_id_or_dms = cur.execute(
        "SELECT count(*) FROM records WHERE json_extract(data, '$._id') IS NOT NULL OR json_extract(data, '$.dms') IS NOT NULL"
    ).fetchone()[0]
    assert records_with_id_or_dms == 0, f"Expected 0 records with _id or dms, got {records_with_id_or_dms}"

    # Verify newly added records have is_new == True
    new_records = cur.execute(
        "SELECT id, data FROM records WHERE json_extract(data, '$.is_new') = 1"
    ).fetchall()
    assert len(new_records) == 4, f"Expected exactly 4 newly added records flagged with is_new, got {len(new_records)}"
    for rid, d_str in new_records:
        assert rid >= 1217, f"Newly added record should have id >= 1217, got {rid}"
        data = json.loads(d_str)
        assert data.get("is_new") is True
        assert data.get("maker") == "MAN B&W"
        assert data.get("breadcrumb") == "Maker Circulars > MAN B&W > 2026"

    # Verify original excel records do NOT have is_new
    excel_new_count = cur.execute(
        "SELECT count(*) FROM records WHERE id <= 1216 AND json_extract(data, '$.is_new') IS NOT NULL"
    ).fetchone()[0]
    assert excel_new_count == 0, f"Expected 0 original excel records flagged as is_new, got {excel_new_count}"
        
    conn.close()
    print("  [PASS] _id and dms successfully removed from schema, column_definitions, and all records.")
    print("  [PASS] Newly added records (apart from Excel data) accurately flagged with is_new: True.")

def test_3_pdf_links_accessibility():
    print("\n=== Test 3: PDF Links Accessibility ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for new_id in [1217, 1218, 1219, 1220]:
        row = cur.execute("SELECT json_extract(data, '$.document_link'), json_extract(data, '$.document_name') FROM records WHERE id = ?", (new_id,)).fetchone()
        url, name = row
        is_valid, final_url, size = verify_pdf_link(url)
        assert is_valid, f"PDF link not accessible for {name}: {url}"
        assert size > 0, f"File size should be > 0: {size}"
        print(f"  [PASS] Accessible PDF: {name[:30]}... ({size} bytes) -> {url}")
    conn.close()

def test_4_idempotency():
    print("\n=== Test 4: Idempotency (Repeatable Execution) ===")
    result = reconcile(dry_run=False)
    assert result["inserted_count"] == 0, f"Expected 0 inserts on repeat, got {result['inserted_count']}"
    assert result["already_present_count"] == 22, f"Expected 22 already present, got {result['already_present_count']}"
    assert result["needs_review_count"] == 2, f"Expected 2 needs review (TOC), got {result['needs_review_count']}"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    count = cur.execute("SELECT count(*) FROM records").fetchone()[0]
    assert count == 1220, f"Expected row count 1220, got {count}"
    conn.close()
    print("  [PASS] Re-running synchronization is completely idempotent: 0 duplicates inserted.")

def test_5_api_endpoints():
    print("\n=== Test 5: API Endpoints Integration ===")
    client = httpx.Client(base_url="http://127.0.0.1:8000")
    
    # 1. Stats
    stats = client.get("/api/stats", params={"dataset_id": 1}).json()
    assert stats["total_records"] == 1220
    assert stats["docs_with_links"] == 1220
    assert stats["newly_added_records"] == 4, f"Expected 4 newly added records, got {stats['newly_added_records']}"
    
    # 2. Maker filter
    resp = client.get("/api/records", params={"dataset_id": 1, "maker": "MAN B&W", "page": 1, "page_size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 294
    for it in data["items"]:
        assert "_id" not in it["data"]
        assert "dms" not in it["data"]

    # 3. Only New filter endpoint
    only_new_resp = client.get("/api/records", params={"dataset_id": 1, "only_new": True})
    assert only_new_resp.status_code == 200
    only_new_data = only_new_resp.json()
    assert only_new_data["total"] == 4, f"Expected 4 only_new records, got {only_new_data['total']}"
    for it in only_new_data["items"]:
        assert it["data"]["is_new"] is True
        assert it["data"]["maker"] == "MAN B&W"
    
    # 4. Search for newly inserted SL2026-790
    search_resp = client.get("/api/records", params={"dataset_id": 1, "search": "SL2026-790"})
    assert search_resp.status_code == 200
    items = search_resp.json()["items"]
    assert len(items) == 1
    assert items[0]["data"]["document_name"] == "SL2026-790: Corrosion behaviour and maintenance guideline for heat shield on injection valves"
    assert items[0]["data"]["document_link"].startswith("https://www.everllence.com/")
    assert items[0]["data"]["is_new"] is True
    
    print("  [PASS] API returned correct stats, newly_added_records count, only_new filter, and clean data objects.")

if __name__ == "__main__":
    test_1_extract_live_page()
    test_2_database_integrity_and_fields()
    test_3_pdf_links_accessibility()
    test_4_idempotency()
    test_5_api_endpoints()
    print("\n" + "=" * 60)
    print("  ALL 5 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
