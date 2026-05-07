"""
AutoCinema Database Layer
SQLite async database for project state persistence.
"""

import os
import json
import uuid
import aiosqlite
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "autocinema.db")


async def get_db():
    """Get an async database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                script TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                voice_name TEXT DEFAULT 'female_warm',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS segments (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                seg_index INTEGER NOT NULL,
                narration_text TEXT NOT NULL DEFAULT '',
                visual_prompt TEXT NOT NULL DEFAULT '',
                motion_prompt TEXT NOT NULL DEFAULT '',
                duration REAL DEFAULT 5.0,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                segment_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                model_name TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                url TEXT DEFAULT '',
                selected INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (segment_id) REFERENCES segments(id) ON DELETE CASCADE
            );
        """)
        await db.commit()
    finally:
        await db.close()


# ── Project CRUD ──────────────────────────────────────────────

async def create_project(name: str, script: str = "") -> dict:
    """Create a new project and return it."""
    db = await get_db()
    try:
        project_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        await db.execute(
            "INSERT INTO projects (id, name, script, status, created_at, updated_at) VALUES (?, ?, ?, 'draft', ?, ?)",
            (project_id, name, script, now, now)
        )
        await db.commit()
        return {"id": project_id, "name": name, "script": script, "status": "draft", "created_at": now, "updated_at": now}
    finally:
        await db.close()


async def get_project(project_id: str) -> dict | None:
    """Get a single project with its segments and assets."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        project = dict(row)

        # Fetch segments
        cursor = await db.execute(
            "SELECT * FROM segments WHERE project_id = ? ORDER BY seg_index",
            (project_id,)
        )
        segments = [dict(r) for r in await cursor.fetchall()]

        # Fetch assets for each segment
        for seg in segments:
            cursor = await db.execute(
                "SELECT * FROM assets WHERE segment_id = ? ORDER BY created_at",
                (seg["id"],)
            )
            assets = [dict(a) for a in await cursor.fetchall()]
            for a in assets:
                if a.get("metadata"):
                    try:
                        a["metadata"] = json.loads(a["metadata"])
                    except:
                        a["metadata"] = {}
            seg["assets"] = assets

        project["segments"] = segments
        return project
    finally:
        await db.close()


async def list_projects() -> list:
    """List all projects (without segments)."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def update_project(project_id: str, **kwargs) -> dict | None:
    """Update project fields."""
    db = await get_db()
    try:
        allowed = {"name", "script", "status", "voice_name"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return await get_project(project_id)
        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [project_id]
        await db.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        await db.commit()
        return await get_project(project_id)
    finally:
        await db.close()


async def delete_project(project_id: str):
    """Delete a project and all related data."""
    db = await get_db()
    try:
        await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await db.commit()
    finally:
        await db.close()


# ── Segment CRUD ──────────────────────────────────────────────

async def create_segments(project_id: str, segments_data: list[dict]) -> list[dict]:
    """Bulk-create segments for a project (replaces existing)."""
    db = await get_db()
    try:
        # Clear old segments first
        await db.execute("DELETE FROM segments WHERE project_id = ?", (project_id,))

        created = []
        for i, seg in enumerate(segments_data):
            seg_id = f"{project_id}_seg{i}"
            await db.execute(
                "INSERT INTO segments (id, project_id, seg_index, narration_text, visual_prompt, motion_prompt, duration) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    seg_id, project_id, i,
                    seg.get("narration_text", ""),
                    seg.get("visual_prompt", ""),
                    seg.get("motion_prompt", ""),
                    seg.get("duration", 5.0)
                )
            )
            created.append({
                "id": seg_id, "project_id": project_id, "seg_index": i,
                "narration_text": seg.get("narration_text", ""),
                "visual_prompt": seg.get("visual_prompt", ""),
                "motion_prompt": seg.get("motion_prompt", ""),
                "duration": seg.get("duration", 5.0),
                "status": "pending", "assets": []
            })

        await db.execute(
            "UPDATE projects SET status = 'analyzed', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), project_id)
        )
        await db.commit()
        return created
    finally:
        await db.close()


async def update_segment(segment_id: str, **kwargs):
    """Update a segment's fields."""
    db = await get_db()
    try:
        allowed = {"narration_text", "visual_prompt", "motion_prompt", "duration", "status"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [segment_id]
        await db.execute(f"UPDATE segments SET {set_clause} WHERE id = ?", values)
        await db.commit()
    finally:
        await db.close()


# ── Asset CRUD ────────────────────────────────────────────────

async def create_asset(segment_id: str, asset_type: str, model_name: str = "",
                       file_path: str = "", url: str = "", selected: bool = False,
                       metadata: dict = None) -> dict:
    """Create an asset record."""
    db = await get_db()
    try:
        asset_id = str(uuid.uuid4())[:12]
        now = datetime.utcnow().isoformat()
        meta_json = json.dumps(metadata or {})
        await db.execute(
            "INSERT INTO assets (id, segment_id, asset_type, model_name, file_path, url, selected, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (asset_id, segment_id, asset_type, model_name, file_path, url, int(selected), meta_json, now)
        )
        await db.commit()
        return {
            "id": asset_id, "segment_id": segment_id, "asset_type": asset_type,
            "model_name": model_name, "file_path": file_path, "url": url,
            "selected": selected, "metadata": metadata or {}, "created_at": now
        }
    finally:
        await db.close()


async def select_asset(asset_id: str, segment_id: str, asset_type: str):
    """Mark one asset as selected, deselect others of the same type in the segment."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE assets SET selected = 0 WHERE segment_id = ? AND asset_type = ?",
            (segment_id, asset_type)
        )
        await db.execute("UPDATE assets SET selected = 1 WHERE id = ?", (asset_id,))
        await db.commit()
    finally:
        await db.close()
