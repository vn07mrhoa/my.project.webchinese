import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.database import (
    search_words,
    get_word_by_id,
    get_words_by_hsk,
    add_to_notebook,
    remove_from_notebook,
    get_notebook,
    get_flashcards,
    review_flashcard,
    get_quizzes,
    save_quiz_result,
    get_stats,
    get_all_topics,
    get_topic_by_id
)

app = FastAPI(title="Hanzii Web Clone", description="API tra từ, luyện viết, ôn tập SRS và bài tập tiếng Trung", version="1.0.0")

@app.on_event("startup")
def startup_event():
    from app.database import init_db, get_connection
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    conn.close()
    if count == 0:
        try:
            from app.seed_full_data import seed_full_system
            from app.init_topics import seed_topics
            seed_full_system()
            seed_topics()
        except Exception as e:
            print("Auto seed error:", e)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Models
class NotebookRequest(BaseModel):
    custom_note: Optional[str] = ""
    tags: Optional[str] = "chung"

class ReviewRequest(BaseModel):
    rating: int  # 1: Quên, 2: Tạm nhớ, 3: Nhớ tốt, 4: Rất dễ

class QuizSubmitRequest(BaseModel):
    level: int
    quiz_type: str
    score: int
    total: int
    details: List[Dict[str, Any]]

# --- API Endpoints ---

@app.get("/api/search")
def api_search(q: str = Query(..., min_length=1, description="Từ khóa tra cứu (Hán tự, Pinyin, Hán Việt, Tiếng Việt)")):
    results = search_words(q)
    return {"query": q, "count": len(results), "data": results}

@app.get("/api/words/{word_id}")
def api_get_word(word_id: int):
    word = get_word_by_id(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ vựng")
    return word

@app.get("/api/hsk/{level}")
def api_get_hsk(level: int, limit: int = 50, offset: int = 0):
    if level < 1 or level > 6:
        raise HTTPException(status_code=400, detail="Cấp độ HSK phải từ 1 đến 6")
    words = get_words_by_hsk(level, limit=limit, offset=offset)
    return {"level": level, "count": len(words), "data": words}

@app.get("/api/notebook")
def api_get_notebook():
    items = get_notebook()
    return {"count": len(items), "data": items}

@app.post("/api/notebook/{word_id}")
def api_add_notebook(word_id: int, req: Optional[NotebookRequest] = None):
    custom_note = req.custom_note if req else ""
    tags = req.tags if req else "chung"
    success = add_to_notebook(word_id, custom_note=custom_note, tags=tags)
    if not success:
        raise HTTPException(status_code=400, detail="Không thể thêm vào sổ tay")
    return {"message": "Đã thêm vào sổ tay", "word_id": word_id}

@app.delete("/api/notebook/{word_id}")
def api_remove_notebook(word_id: int):
    remove_from_notebook(word_id)
    return {"message": "Đã xóa khỏi sổ tay", "word_id": word_id}

@app.get("/api/flashcards")
def api_get_flashcards(filter: str = "due", level: Optional[int] = None):
    cards = get_flashcards(filter_type=filter, level=level)
    return {"filter": filter, "count": len(cards), "data": cards}

@app.post("/api/flashcards/{word_id}/review")
def api_review_card(word_id: int, req: ReviewRequest):
    if req.rating not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Điểm đánh giá phải từ 1 đến 4")
    result = review_flashcard(word_id, req.rating)
    return {"message": "Đã ghi nhận kết quả ôn tập", "card": result}

@app.get("/api/quizzes")
def api_get_quizzes(level: Optional[int] = 0, type: Optional[str] = "all", difficulty: Optional[str] = "all", count: int = 15):
    quizzes = get_quizzes(level=level, quiz_type=type, difficulty=difficulty, count=count)
    return {"level": level, "type": type, "difficulty": difficulty, "count": len(quizzes), "data": quizzes}

@app.post("/api/quizzes/submit")
def api_submit_quiz(req: QuizSubmitRequest):
    history_id = save_quiz_result(
        user_id="default_user",
        level=req.level,
        quiz_type=req.quiz_type,
        score=req.score,
        total=req.total,
        details=req.details
    )
    return {
        "message": "Đã lưu kết quả bài tập",
        "history_id": history_id,
        "score": req.score,
        "total": req.total,
        "percentage": round(req.score / req.total * 100, 1) if req.total > 0 else 0
    }

@app.get("/api/stats")
def api_get_stats():
    return get_stats()

@app.get("/api/topics")
def api_get_topics():
    topics = get_all_topics()
    return {"count": len(topics), "data": topics}

@app.get("/api/topics/{topic_id}")
def api_get_topic_detail(topic_id: int):
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")
    return topic

# Mount frontend static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Hanzii Web API đang hoạt động! Đang tải frontend..."}
