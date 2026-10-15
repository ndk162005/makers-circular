import sqlite3
import json
import shutil
import os
import datetime

ROOT_DIR = r"c:\Users\Dhureen-Intern\Downloads\maker-circulars-website\maker-circulars-website"
DB_PATH = os.path.join(ROOT_DIR, "data", "maker_circulars.db")
BACKUP_DIR = os.path.join(ROOT_DIR, "data", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# 1. Create Backup
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(BACKUP_DIR, f"maker_circulars_backup_before_add_date_{timestamp}.db")
shutil.copy2(DB_PATH, backup_path)
print(f"[BACKUP] Created backup at {backup_path}")

# 2. Open connection and begin transaction
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    # 2a. Update column_definitions
    print("\n[MIGRATION] Checking column_definitions...")
    existing_col = cur.execute(
        "SELECT id FROM column_definitions WHERE dataset_id = 1 AND name = 'date_of_upload'"
    ).fetchone()
    
    if not existing_col:
        cur.execute(
            "INSERT INTO column_definitions (dataset_id, name, data_type, position, is_active) VALUES (1, 'date_of_upload', 'date', 4, 1)"
        )
        print("  Added 'date_of_upload' to column_definitions.")
    else:
        print("  'date_of_upload' already exists in column_definitions.")

    col_defs = cur.execute("SELECT id, name, position, is_active FROM column_definitions WHERE dataset_id = 1").fetchall()
    print("  Current column definitions:", col_defs)

    # 2b. Update datasets
    print("\n[MIGRATION] Updating datasets...")
    col_names = ['maker', 'breadcrumb', 'document_name', 'document_link', 'date_of_upload']
    cur.execute(
        "UPDATE datasets SET column_count = ?, column_names = ? WHERE id = 1",
        (len(col_names), json.dumps(col_names))
    )
    dataset_info = cur.execute("SELECT id, column_count, column_names FROM datasets WHERE id = 1").fetchone()
    print("  Updated dataset:", dataset_info)

    # 2c. Update records
    print("\n[MIGRATION] Updating records data...")
    records = cur.execute("SELECT id, created_at, data FROM records").fetchall()
    print(f"  Processing {len(records)} records...")
    
    updated_new_count = 0
    blank_count = 0

    for rid, created_at, data_str in records:
        data = json.loads(data_str)
        is_new = bool(data.get("is_new") or rid >= 1217)

        if is_new:
            # Extract date of upload from created_at
            if created_at:
                upload_date = created_at.split("T")[0].split(" ")[0]
            else:
                upload_date = "2026-10-12"
            data["date_of_upload"] = upload_date
            updated_new_count += 1
        else:
            # Leave blank for the rest (Excel records)
            data["date_of_upload"] = ""
            blank_count += 1

        cur.execute(
            "UPDATE records SET data = ? WHERE id = ?",
            (json.dumps(data), rid)
        )

    conn.commit()
    print(f"[MIGRATION] Committed successfully!")
    print(f"  Records with upload date populated: {updated_new_count}")
    print(f"  Records with upload date left blank: {blank_count}")

    # Inspect sample records
    print("\nSample Excel record (id 1):")
    r1 = cur.execute("SELECT id, data FROM records WHERE id = 1").fetchone()
    print(" ", r1)

    print("\nSample newly added record (id 1217):")
    r_new = cur.execute("SELECT id, data FROM records WHERE id = 1217").fetchone()
    print(" ", r_new)

except Exception as e:
    conn.rollback()
    print(f"[ERROR] Migration failed and rolled back: {e}")
    raise e
finally:
    conn.close()

print("\n[SUCCESS] Migration completed successfully!")
