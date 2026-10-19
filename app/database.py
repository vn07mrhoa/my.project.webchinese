import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "hanzii.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Bảng từ vựng (Words)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simplified TEXT NOT NULL UNIQUE,
        traditional TEXT,
        pinyin TEXT NOT NULL,
        pinyin_clean TEXT,
        hanviet TEXT NOT NULL,
        meaning TEXT NOT NULL,
        hsk_level INTEGER DEFAULT 1,
        radical TEXT,
        stroke_count INTEGER DEFAULT 0,
        part_of_speech TEXT,
        examples TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Chỉ mục tìm kiếm nhanh
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_simplified ON words(simplified);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pinyin ON words(pinyin);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pinyin_clean ON words(pinyin_clean);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hanviet ON words(hanviet);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hsk ON words(hsk_level);")

    # Bảng Sổ tay từ vựng (Notebook)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notebook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL UNIQUE,
        user_id TEXT DEFAULT 'default_user',
        custom_note TEXT,
        tags TEXT DEFAULT 'chung',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
    );
    """)

    # Bảng Flashcard ôn tập (SRS - Spaced Repetition System)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL UNIQUE,
        user_id TEXT DEFAULT 'default_user',
        repetition INTEGER DEFAULT 0,
        interval_days INTEGER DEFAULT 1,
        ease_factor REAL DEFAULT 2.5,
        next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new', -- 'new', 'learning', 'mastered'
        last_reviewed TIMESTAMP,
        FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
    );
    """)

    # Bảng Bài tập & Câu hỏi trắc nghiệm (Quizzes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER DEFAULT 1,
        type TEXT NOT NULL, -- 'meaning', 'pinyin', 'hanzi', 'listening'
        question TEXT NOT NULL,
        target_word TEXT,
        pinyin_hint TEXT,
        options TEXT NOT NULL, -- JSON array
        correct_index INTEGER NOT NULL,
        explanation TEXT
    );
    """)

    # Bảng Bài học theo chủ đề (Topics / Lessons)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'Giao tiếp cơ bản',
        description TEXT,
        level INTEGER DEFAULT 1,
        vocabularies TEXT DEFAULT '[]', -- JSON array of vocab
        dialogues TEXT DEFAULT '[]',    -- JSON array of dialogues
        grammar TEXT DEFAULT '[]',      -- JSON array of grammar notes
        quizzes TEXT DEFAULT '[]',      -- JSON array of mini quiz questions
        is_locked INTEGER DEFAULT 0,
        order_num INTEGER DEFAULT 1
    );
    """)

    # Bảng Lịch sử làm bài tập
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'default_user',
        level INTEGER,
        quiz_type TEXT,
        score INTEGER,
        total INTEGER,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

# Helper queries
def search_words(query: str, limit: int = 30) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = query.strip()
    clean_q = query.lower()

    sql = """
    SELECT w.*, (CASE WHEN n.id IS NOT NULL THEN 1 ELSE 0 END) as is_favorited
    FROM words w
    LEFT JOIN notebook n ON w.id = n.word_id
    WHERE w.simplified LIKE ? 
       OR w.traditional LIKE ?
       OR w.pinyin LIKE ?
       OR w.pinyin_clean LIKE ?
       OR w.hanviet LIKE ?
       OR w.meaning LIKE ?
    ORDER BY 
       CASE 
         WHEN w.simplified = ? THEN 1
         WHEN w.simplified LIKE ? THEN 2
         WHEN w.pinyin LIKE ? THEN 3
         ELSE 4
       END,
       w.hsk_level ASC,
       w.id ASC
    LIMIT ?
    """
    pattern = f"%{query}%"
    cursor.execute(sql, (
        pattern, pattern, pattern, f"%{clean_q}%", pattern, pattern,
        query, f"{query}%", f"{clean_q}%", limit
    ))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["examples"] = json.loads(item["examples"] or "[]")
        except:
            item["examples"] = []
        results.append(item)
    conn.close()
    return results

def get_word_by_id(word_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT w.*, (CASE WHEN n.id IS NOT NULL THEN 1 ELSE 0 END) as is_favorited
    FROM words w
    LEFT JOIN notebook n ON w.id = n.word_id
    WHERE w.id = ?
    """, (word_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    try:
        res["examples"] = json.loads(res["examples"] or "[]")
    except:
        res["examples"] = []
    return res

def get_words_by_hsk(level: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT w.*, (CASE WHEN n.id IS NOT NULL THEN 1 ELSE 0 END) as is_favorited
    FROM words w
    LEFT JOIN notebook n ON w.id = n.word_id
    WHERE w.hsk_level = ?
    ORDER BY w.id ASC
    LIMIT ? OFFSET ?
    """, (level, limit, offset))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["examples"] = json.loads(item["examples"] or "[]")
        except:
            item["examples"] = []
        results.append(item)
    conn.close()
    return results

# Notebook
def add_to_notebook(word_id: int, custom_note: str = "", tags: str = "chung") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO notebook (word_id, custom_note, tags)
        VALUES (?, ?, ?)
        """, (word_id, custom_note, tags))
        # Đồng thời tạo thẻ flashcard nếu chưa có
        cursor.execute("""
        INSERT OR IGNORE INTO flashcards (word_id, next_review, status)
        VALUES (?, CURRENT_TIMESTAMP, 'new')
        """, (word_id,))
        conn.commit()
        return True
    except Exception as e:
        print("add_to_notebook error:", e)
        return False
    finally:
        conn.close()

def remove_from_notebook(word_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notebook WHERE word_id = ?", (word_id,))
    conn.commit()
    conn.close()
    return True

def get_notebook() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT n.id as notebook_id, n.custom_note, n.tags, n.created_at as saved_at,
           w.*, 1 as is_favorited,
           f.status as flashcard_status, f.repetition as review_count
    FROM notebook n
    JOIN words w ON n.word_id = w.id
    LEFT JOIN flashcards f ON w.id = f.word_id
    ORDER BY n.id DESC
    """)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["examples"] = json.loads(item["examples"] or "[]")
        except:
            item["examples"] = []
        results.append(item)
    conn.close()
    return results

# Flashcards & SRS
def get_flashcards(filter_type: str = "due", level: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT f.*, w.simplified, w.traditional, w.pinyin, w.hanviet, w.meaning, 
           w.hsk_level, w.radical, w.stroke_count, w.examples
    FROM flashcards f
    JOIN words w ON f.word_id = w.id
    WHERE 1=1
    """
    params = []
    if level:
        query += " AND w.hsk_level = ?"
        params.append(level)
    
    if filter_type == "due":
        query += " AND (f.next_review <= CURRENT_TIMESTAMP OR f.status = 'new')"
    elif filter_type == "mastered":
        query += " AND f.status = 'mastered'"
    elif filter_type == "learning":
        query += " AND f.status = 'learning'"
        
    query += " ORDER BY f.next_review ASC LIMIT 50"
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["examples"] = json.loads(item["examples"] or "[]")
        except:
            item["examples"] = []
        results.append(item)
    conn.close()
    return results

def review_flashcard(word_id: int, rating: int) -> Dict[str, Any]:
    """
    rating: 
    1: Quên (Forgot - reset)
    2: Khó/Tạm nhớ (Hard - +1 ngày)
    3: Nhớ tốt (Good - SRS standard)
    4: Rất dễ/Đã thuộc (Easy - bonus interval)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashcards WHERE word_id = ?", (word_id,))
    row = cursor.fetchone()
    
    if not row:
        # Tạo mới nếu chưa có
        cursor.execute("INSERT INTO flashcards (word_id) VALUES (?)", (word_id,))
        conn.commit()
        cursor.execute("SELECT * FROM flashcards WHERE word_id = ?", (word_id,))
        row = cursor.fetchone()

    card = dict(row)
    repetition = card["repetition"]
    interval = card["interval_days"]
    ease_factor = card["ease_factor"]
    
    if rating == 1:
        repetition = 0
        interval = 1
        status = "learning"
    else:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 3
        else:
            bonus = 1.3 if rating == 4 else 1.0
            interval = int(interval * ease_factor * bonus)
        repetition += 1
        status = "mastered" if repetition >= 4 else "learning"

    # Điều chỉnh ease factor (SM-2 variant)
    ease_factor = ease_factor + (0.1 - (4 - rating) * (0.08 + (4 - rating) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    next_date = (datetime.utcnow() + timedelta(days=interval)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
    UPDATE flashcards
    SET repetition = ?, interval_days = ?, ease_factor = ?, next_review = ?,
        status = ?, last_reviewed = CURRENT_TIMESTAMP
    WHERE word_id = ?
    """, (repetition, interval, ease_factor, next_date, status, word_id))
    
    conn.commit()
    conn.close()
    return {
        "word_id": word_id,
        "repetition": repetition,
        "interval_days": interval,
        "status": status,
        "next_review": next_date
    }

# Quizzes
def get_quizzes(level: Optional[int] = None, quiz_type: Optional[str] = None, difficulty: Optional[str] = None, count: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM quizzes WHERE 1=1"
    params = []
    if level and level > 0:
        query += " AND level = ?"
        params.append(level)
    if quiz_type and quiz_type != "all":
        query += " AND type = ?"
        params.append(quiz_type)
    if difficulty and difficulty != "all":
        query += " AND difficulty = ?"
        params.append(difficulty)
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(count)
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["options"] = json.loads(item["options"] or "[]")
        except:
            item["options"] = []
        try:
            item["extra_data"] = json.loads(item.get("extra_data") or "{}")
        except:
            item["extra_data"] = {}
        results.append(item)
    conn.close()
    return results

def save_quiz_result(user_id: str, level: int, quiz_type: str, score: int, total: int, details: List[Dict[str, Any]]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO quiz_history (user_id, level, quiz_type, score, total, details)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, level, quiz_type, score, total, json.dumps(details, ensure_ascii=False)))
    history_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return history_id

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM words")
    total_words = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notebook")
    notebook_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flashcards WHERE status = 'mastered'")
    mastered_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    total_quizzes = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(score * 100.0 / total), COUNT(*) FROM quiz_history")
    row = cursor.fetchone()
    avg_score = round(row[0] or 0, 1)
    quizzes_taken = row[1] or 0
    
    conn.close()
    return {
        "total_words": total_words,
        "notebook_count": notebook_count,
        "mastered_count": mastered_count,
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "quizzes_taken": quizzes_taken
    }

# Topics / Lessons By Theme
def get_all_topics() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, title, category, description, level, is_locked, order_num,
           json_array_length(vocabularies) as vocab_count,
           json_array_length(dialogues) as dialogue_count
    FROM topics
    ORDER BY order_num ASC
    """)
    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results

def get_topic_by_id(topic_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    for field in ["vocabularies", "dialogues", "grammar", "quizzes"]:
        try:
            res[field] = json.loads(res[field] or "[]")
        except:
            res[field] = []
    return res

