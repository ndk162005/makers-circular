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
backup_path = os.path.join(BACKUP_DIR, f"maker_circulars_backup_before_remove_id_dms_{timestamp}.db")
shutil.copy2(DB_PATH, backup_path)
print(f"[BACKUP] Created backup at {backup_path}")

# 2. Open connection and begin transaction
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    # 2a. Update column_definitions
    print("\n[MIGRATION] Updating column_definitions...")
    cur.execute("DELETE FROM column_definitions WHERE name IN ('_id', 'id', 'dms')")
    
    # Update remaining positions
    remaining_cols = ['maker', 'breadcrumb', 'document_name', 'document_link']
    for pos, col_name in enumerate(remaining_cols):
        cur.execute("UPDATE column_definitions SET position = ? WHERE name = ?", (pos, col_name))
    
    cur_cols = cur.execute("SELECT id, name, position, is_active FROM column_definitions").fetchall()
    print("  Remaining column definitions:", cur_cols)

    # 2b. Update datasets
    print("\n[MIGRATION] Updating datasets...")
    cur.execute(
        "UPDATE datasets SET column_count = 4, column_names = ? WHERE id = 1",
        (json.dumps(remaining_cols),)
    )
    dataset_info = cur.execute("SELECT id, column_count, column_names FROM datasets WHERE id = 1").fetchone()
    print("  Updated dataset:", dataset_info)

    # 2c. Update records
    print("\n[MIGRATION] Updating records data...")
    records = cur.execute("SELECT id, data FROM records").fetchall()
    print(f"  Processing {len(records)} records...")
    
    updated_count = 0
    newly_flagged_count = 0

    for rid, data_str in records:
        data = json.loads(data_str)
        changed = False

        # Remove _id and dms
        if "_id" in data:
            del data["_id"]
            changed = True
        if "dms" in data:
            del data["dms"]
            changed = True

        # Flag newly added records (apart from Excel data)
        # Original Excel records have id <= 1216
        # Newly synchronized / added records have id >= 1217
        if rid >= 1217:
            data["is_new"] = True
            newly_flagged_count += 1
            changed = True
        else:
            if "is_new" in data:
                del data["is_new"]
                changed = True

        if changed:
            cur.execute(
                "UPDATE records SET data = ? WHERE id = ?",
                (json.dumps(data), rid)
            )
            updated_count += 1

    conn.commit()
    print(f"[MIGRATION] Committed! Total records updated: {updated_count}")
    print(f"[MIGRATION] Records flagged as newly added (is_new=True): {newly_flagged_count}")

    # Verify sample records
    r1 = cur.execute("SELECT id, data FROM records WHERE id = 1").fetchone()
    print("\nSample Excel record (id 1):", r1)
    r_new = cur.execute("SELECT id, data FROM records WHERE id = 1217").fetchone()
    print("Sample newly added record (id 1217):", r_new)

except Exception as e:
    conn.rollback()
    print(f"[ERROR] Migration failed and rolled back: {e}")
    raise e
finally:
    conn.close()

print("\n[SUCCESS] Migration completed successfully!")
