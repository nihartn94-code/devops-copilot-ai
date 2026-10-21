import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiosqlite
from backend.app.config import settings

def get_db_path() -> str:
    # Resolve relative to project root
    p = Path(settings.db_path)
    if not p.is_absolute():
        project_root = Path(__file__).resolve().parent.parent.parent
        p = project_root / settings.db_path
    return str(p)

_initialized = False

async def init_db():
    global _initialized
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                raw_input TEXT NOT NULL,
                structured_output TEXT NOT NULL,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                secrets_redacted_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                analysis_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id, created_at ASC)")
        await db.commit()
    _initialized = True

async def ensure_db():
    global _initialized
    if not _initialized:
        await init_db()

async def save_analysis(
    analysis_id: str,
    analysis_type: str,
    title: str,
    summary: str,
    raw_input: str,
    structured_output: Dict[str, Any],
    provider: str,
    model_id: str,
    secrets_redacted_count: int = 0
) -> Dict[str, Any]:
    await ensure_db()
    db_file = get_db_path()
    created_at = datetime.now(timezone.utc).isoformat()
    json_output = json.dumps(structured_output)

    async with aiosqlite.connect(db_file) as db:
        await db.execute(
            """
            INSERT INTO analyses (
                id, created_at, analysis_type, title, summary,
                raw_input, structured_output, provider, model_id, secrets_redacted_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_id, created_at, analysis_type, title, summary,
                raw_input, json_output, provider, model_id, secrets_redacted_count
            )
        )
        await db.commit()

    return {
        "id": analysis_id,
        "created_at": created_at,
        "analysis_type": analysis_type,
        "title": title,
        "summary": summary,
        "provider": provider,
        "model_id": model_id,
        "secrets_redacted_count": secrets_redacted_count
    }

async def get_analyses(limit: int = 50, offset: int = 0, analysis_type: Optional[str] = None) -> List[Dict[str, Any]]:
    await ensure_db()
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        db.row_factory = aiosqlite.Row
        if analysis_type:
            cursor = await db.execute(
                """
                SELECT id, created_at, analysis_type, title, summary, provider, model_id, secrets_redacted_count
                FROM analyses
                WHERE analysis_type = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (analysis_type, limit, offset)
            )
        else:
            cursor = await db.execute(
                """
                SELECT id, created_at, analysis_type, title, summary, provider, model_id, secrets_redacted_count
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE id = ?",
            (analysis_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res["structured_output"] = json.loads(res["structured_output"])
        except Exception:
            pass
        return res

async def delete_analysis_by_id(analysis_id: str) -> bool:
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        cursor = await db.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        await db.commit()
        return cursor.rowcount > 0

async def get_dashboard_metrics() -> Dict[str, Any]:
    await ensure_db()
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM analyses")
        total_analyses = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM analyses WHERE analysis_type = 'build_log'")
        total_build_logs = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM analyses WHERE analysis_type = 'test_result'")
        total_tests = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM analyses WHERE analysis_type = 'repo_inspection'")
        total_repos = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM analyses WHERE analysis_type = 'doc_search'")
        total_docs = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COALESCE(SUM(secrets_redacted_count), 0) FROM analyses")
        total_secrets_redacted = (await cursor.fetchone())[0]

        cursor = await db.execute(
            """
            SELECT id, created_at, analysis_type, title, summary, provider, model_id
            FROM analyses
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, created_at, analysis_type, title, summary, provider, model_id
            FROM analyses
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        recent_rows = await cursor.fetchall()
        recent = [dict(r) for r in recent_rows]

        return {
            "total_analyses": total_analyses,
            "total_build_logs": total_build_logs,
            "total_tests": total_tests,
            "total_repos": total_repos,
            "total_docs": total_docs,
            "total_secrets_redacted": total_secrets_redacted,
            "recent_analyses": recent
        }

async def save_chat_message(
    message_id: str,
    session_id: str,
    role: str,
    content: str,
    provider: str,
    model_id: str,
    analysis_id: Optional[str] = None
) -> Dict[str, Any]:
    db_file = get_db_path()
    created_at = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_file) as db:
        await db.execute(
            """
            INSERT INTO chat_messages (id, session_id, analysis_id, role, content, created_at, provider, model_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (message_id, session_id, analysis_id, role, content, created_at, provider, model_id)
        )
        await db.commit()
    return {
        "id": message_id,
        "session_id": session_id,
        "analysis_id": analysis_id,
        "role": role,
        "content": content,
        "created_at": created_at,
        "provider": provider,
        "model_id": model_id
    }

async def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    db_file = get_db_path()
    async with aiosqlite.connect(db_file) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, session_id, analysis_id, role, content, created_at, provider, model_id
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
