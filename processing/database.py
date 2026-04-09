import sqlite3
import os
import json
from datetime import datetime
from logger.logger import logger

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'applications.db')

def init_db():
    """Initializes the SQLite database with the applications table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applied_jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            source TEXT,
            apply_link TEXT,
            attention_score REAL,
            matched_skills TEXT,
            applied_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def save_application(job: dict) -> bool:
    """Saves a job application to the database. Returns True if saved, False if already exists."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT job_id FROM applied_jobs WHERE job_id = ?", (job['id'],))
        if cursor.fetchone():
            return False
            
        matched_str = json.dumps(job.get('matched_keywords', []))
        
        cursor.execute('''
            INSERT INTO applied_jobs (job_id, title, company, source, apply_link, attention_score, matched_skills, applied_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job['id'],
            job.get('title', 'Unknown'),
            job.get('company', 'Unknown'),
            job.get('source', 'Unknown'),
            job.get('apply_link', ''),
            job.get('attention_score', 0),
            matched_str,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save application: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_applications() -> list:
    """Retrieves all saved applications from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applied_jobs ORDER BY applied_at DESC")
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            results.append({
                'id': r['job_id'],
                'title': r['title'],
                'company': r['company'],
                'source': r['source'],
                'apply_link': r['apply_link'],
                'attention_score': r['attention_score'],
                'matched_keywords': json.loads(r['matched_skills']),
                'applied_at': r['applied_at']
            })
        return results
    except Exception as e:
        logger.error(f"Failed to get applications: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def delete_application(job_id: str) -> bool:
    """Deletes a saved application from the database by job_id."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applied_jobs WHERE job_id = ?", (job_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to delete application {job_id}: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
