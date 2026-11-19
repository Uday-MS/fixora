"""
FIXORA Safe Database Cleanup & Hygiene Script
Removes duplicate test-polluted records created by test runs while strictly preserving:
- User accounts (e.g. alex.vance@fixora.dev)
- Real connected GitHub repositories (e.g. Uday-MS/AI_Research_paper_exp)
- Legitimate baseline seed data
"""
import sqlite3
import os

DB_PATH = "fixora.db"

def clean_database():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print("--- Starting Safe Database Cleanup ---")

    # 1. Deduplicate repositories by full_name
    # Keep the most recently synced/created one for each unique full_name or url
    cur.execute("""
        SELECT full_name, url, COUNT(*) 
        FROM repositories 
        GROUP BY full_name, url 
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    
    for full_name, url, count in duplicates:
        print(f"Found duplicate repository: {full_name} ({count} copies)")
        # Find all IDs ordered by last_synced_at DESC
        cur.execute("""
            SELECT id FROM repositories 
            WHERE full_name = ? AND url = ? 
            ORDER BY last_synced_at DESC, created_at DESC
        """, (full_name, url))
        all_ids = [r[0] for r in cur.fetchall()]
        keep_id = all_ids[0]
        delete_ids = all_ids[1:]
        print(f"  Keeping ID: {keep_id}, deleting duplicates: {delete_ids}")
        for del_id in delete_ids:
            cur.execute("DELETE FROM bugs WHERE repository_id = ?", (del_id,))
            cur.execute("DELETE FROM patches WHERE repository_id = ?", (del_id,))
            cur.execute("DELETE FROM repositories WHERE id = ?", (del_id,))

    # 2. Delete test-polluted 'sample-microservice' created by automated test runs
    cur.execute("SELECT id FROM repositories WHERE name = 'sample-microservice'")
    test_repo_ids = [r[0] for r in cur.fetchall()]
    if test_repo_ids:
        print(f"Removing {len(test_repo_ids)} test artifact repositories ('sample-microservice')...")
        for tid in test_repo_ids:
            cur.execute("DELETE FROM bugs WHERE repository_id = ?", (tid,))
            cur.execute("DELETE FROM patches WHERE repository_id = ?", (tid,))
            cur.execute("DELETE FROM repositories WHERE id = ?", (tid,))

    # 3. Clean duplicate test projects named 'Checkout Cart Service' from pytest
    cur.execute("SELECT id FROM projects WHERE name = 'Checkout Cart Service'")
    test_proj_ids = [r[0] for r in cur.fetchall()]
    if test_proj_ids:
        print(f"Removing {len(test_proj_ids)} test artifact projects ('Checkout Cart Service')...")
        for pid in test_proj_ids:
            # Delete child repositories first
            cur.execute("SELECT id FROM repositories WHERE project_id = ?", (pid,))
            r_ids = [r[0] for r in cur.fetchall()]
            for rid in r_ids:
                cur.execute("DELETE FROM bugs WHERE repository_id = ?", (rid,))
                cur.execute("DELETE FROM patches WHERE repository_id = ?", (rid,))
                cur.execute("DELETE FROM repositories WHERE id = ?", (rid,))
            cur.execute("DELETE FROM bugs WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM incidents WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM investigations WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM knowledge_documents WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM ingestion_jobs WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM service_nodes WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM telemetry_logs WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM telemetry_metrics WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM telemetry_traces WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM projects WHERE id = ?", (pid,))

    # 4. Clean duplicate/orphaned workspaces not attached to any project
    cur.execute("""
        SELECT id, name FROM workspaces 
        WHERE id != 'ws_demo_001' 
        AND id NOT IN (SELECT DISTINCT workspace_id FROM projects)
    """)
    orphan_ws = cur.fetchall()
    if orphan_ws:
        print(f"Removing {len(orphan_ws)} orphaned test workspaces...")
        for wid, wname in orphan_ws:
            cur.execute("DELETE FROM workspaces WHERE id = ?", (wid,))

    # 5. Clean duplicate organizations created by tests
    cur.execute("""
        SELECT id, name FROM organizations 
        WHERE id != 'org_demo_001' 
        AND id NOT IN (SELECT DISTINCT organization_id FROM workspaces)
    """)
    orphan_orgs = cur.fetchall()
    if orphan_orgs:
        print(f"Removing {len(orphan_orgs)} orphaned test organizations...")
        for oid, oname in orphan_orgs:
            cur.execute("DELETE FROM organization_members WHERE organization_id = ?", (oid,))
            cur.execute("DELETE FROM organizations WHERE id = ?", (oid,))

    conn.commit()
    conn.close()
    print("--- Safe Database Cleanup Complete ---")

if __name__ == "__main__":
    clean_database()
