# 🏮 Hanzii Web Clone - Nền Tảng Học Tiếng Trung & Luyện Thi HSK Toàn Diện

Hệ thống web học tiếng Trung thông minh mô phỏng đầy đủ các tính năng cốt lõi của **Hanzii Dict**, bao gồm tra từ điển đa chiều, xem hoạt họa bút thuận chữ Hán (Stroke Order), bảng tập viết chữ tương tác có chấm điểm nét vẽ, **phân hệ ôn tập Flashcard (Spaced Repetition System - SRS)** và **hệ thống làm bài tập & thi thử HSK có chấm điểm và giải thích chi tiết**.

---

## 🚀 Cách Chạy Nhanh Ứng Dụng (1 Click)

### Cách 1: Chạy bằng file Batch (Windows)
Chỉ cần nhấp đúp vào file:
👉 **`run.bat`**

### Cách 2: Chạy bằng dòng lệnh Terminal
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Sau đó mở trình duyệt truy cập:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🌟 Các Phân Hệ Tính Năng Chính

### 1. 🔍 Tra từ điển đa chiều (Hán - Việt - Pinyin - Bộ thủ - Ví dụ)
- **Tra cứu thông minh:** Hỗ trợ nhập Chữ Hán (Giản thể / Phồn thể), Pinyin có dấu hoặc không dấu (`xuexi`, `ni hao`), Âm Hán Việt (`học tập`, `nhĩ hảo`) hoặc Nghĩa tiếng Việt.
- **Thẻ từ vựng chi tiết chuẩn Hanzii:**
  - Hiển thị chữ to theo font thư pháp truyền thống.
  - Loa phát âm chuẩn tiếng Trung phổ thông (Web Speech API Mandarin `zh-CN`).
  - Âm Hán Việt nổi bật giúp người Việt nhớ từ qua mối liên hệ từ nguyên.
  - Phân tích Bộ thủ (Radical), số nét bút, từ loại.
  - Câu ví dụ song ngữ Trung - Pinyin - Việt kèm nút phát âm từng câu.
  - Nút **"Lưu vào sổ tay"** và **"Luyện viết chữ này"**.

---

### 2. 📚 Học theo từng bài & Chủ đề (Bài học giao tiếp chuẩn Hán ngữ)
- **Danh sách bài học trực quan:** Bám sát giáo trình Hán ngữ thông dụng theo thứ tự:
  - *Bài 1: Chào hỏi (问候)*
  - *Bài 2: Bạn có bận không? (你忙吗？)*
  - *Bài 3: Ngày mai gặp lại (明天见)*
  - *Bài 4: Ngày, Tháng, Năm (日期与时间)*
  - *Bài 5: Bạn đi đâu đấy? (你去哪儿？)*
  - *Bài 6: Giới thiệu hỏi thăm (介绍与问候)*
  - *Bài 7: Bạn ăn gì? (你吃什么？)*
  - *Bài 8: Mua sắm & Giá cả (买东西)*
- **Giao diện bài học chuyên sâu với 4 phân mục:**
  1. **生词 Từ vựng trọng tâm:** Chữ Hán, Pinyin, Hán Việt, giải nghĩa, loa phát âm, nút luyện viết nét chữ, nút lưu vào sổ tay.
  2. **课文 Hội thoại thực tế:** Trình bày dạng bong bóng đối thoại hai nhân vật A - B, có nút nghe liên tục toàn bài và nghe từng câu.
  3. **语法 Điểm ngữ pháp cốt lõi:** Phân tích công thức câu kèm ví dụ song ngữ dễ hiểu.
  4. **📝 Bài tập củng cố:** Câu hỏi trắc nghiệm kiểm tra mức độ tiếp thu ngay sau bài học.
- **Hỗ trợ mở khóa linh hoạt:** Trạng thái khóa/mở khóa học thử tiện lợi.

---

### 3. ✍️ Luyện viết chữ Hán tương tác (Stroke Order & Writing Practice)
- Tích hợp thư viện **HanziWriter** kết hợp khung chữ điền chuẩn thư pháp **Tian Zi Ge (田字格 / 米字格)**.
- **3 Chế độ hoạt động:**
  1. **▶️ Xem nét vẽ mẫu (Animate):** Chạy tự động thứ tự từng nét viết theo chuẩn quy tắc bút thuận.
  2. **👁️ Bật/Tắt đường nét mờ (Outline):** Hỗ trợ người mới bắt đầu dễ quan sát tỷ lệ chữ.
  3. **✍️ Tự tập viết (Interactive Quiz Mode):** Người học dùng chuột hoặc ngón tay cảm ứng để đồ trực tiếp lên khung vẽ. Hệ thống tự động chấm đúng/sai từng nét, cảnh báo sai nét, hướng dẫn sau 3 lần sai và bắn hiệu ứng pháo hoa khi hoàn thành chữ!

---

### 3. 🗂️ Phân Hệ Ôn Tập Flashcard Thông Minh (SRS - Spaced Repetition)
- Áp dụng phương pháp ghi nhớ ngắt quãng khoa học (**SM-2 / Leitner Algorithm**).
- **Thẻ lật 3D tương tác:**
  - *Mặt trước:* Chữ Hán to bản, phát âm, số nét, cấp độ HSK.
  - *Mặt sau:* Phiên âm Pinyin, âm Hán Việt, định nghĩa đầy đủ, câu ví dụ.
- **Hệ thống chấm điểm 4 mức độ nhớ:**
  - 🔴 **1. Quên:** Reset chu kỳ, ôn lại ngay lập tức.
  - 🟡 **2. Khó:** Nhớ một phần, dời chu kỳ +1 ngày.
  - 🟢 **3. Nhớ tốt:** Thuộc chuẩn, tăng chu kỳ theo hệ số Ease Factor (+3 ngày).
  - 🟣 **4. Rất dễ:** Hoàn toàn làm chủ từ vựng, tăng tốc chu kỳ (+7 ngày).
- Thanh đo tiến độ ôn tập thời gian thực và tự động đưa từ vào trạng thái **"Đã thuộc" (Mastered)** khi ôn thành công nhiều lần.

---

### 4. 📝 Phân Hệ Làm Bài Tập & Luyện Thi Thử HSK
- Phân loại theo cấp độ: **HSK 1, HSK 2, HSK 3, HSK 4, HSK 5, HSK 6**.
- Đa dạng các dạng câu hỏi kiểm tra:
  - **Nghĩa của từ:** Từ chữ Hán suy ra nghĩa tiếng Việt.
  - **Phiên âm Pinyin:** Nhận diện đúng thanh điệu và cách đọc.
  - **Nhận diện chữ Hán:** Đọc câu/nghĩa để chọn chữ Hán chính xác.
  - **Luyện nghe & chọn từ:** Nghe âm thanh phát âm và chọn đáp án tương ứng.
- **Phản hồi tức thì (Instant Feedback):**
  - Đổi màu xanh/đỏ trực tiếp khi bấm chọn.
  - Hộp giải thích ngữ nghĩa chi tiết vì sao đáp án đó đúng.
- **Bảng tổng kết bài thi:**
  - Tính điểm và tỷ lệ % chính xác.
  - Đánh giá năng lực và phân tích các câu làm sai.

---

### 5. 📖 Sổ tay từ vựng cá nhân (Notebook)
- Lưu trữ mọi từ vựng người dùng đánh dấu sao trong lúc tra từ hoặc làm bài tập.
- Tự động đồng bộ hóa với hệ thống thẻ Flashcard SRS.
- Hỗ trợ thêm ghi chú cá nhân, xóa từ hoặc chuyển sang luyện viết chỉ với 1 click.

---

## 🏗️ Cấu Trúc Dự Án

```
Antigravity/
├── app/
│   ├── main.py              # FastAPI Web Server & REST API
│   ├── database.py          # Kết nối SQLite & các hàm xử lý dữ liệu
│   ├── init_data.py         # Nạp kho từ vựng HSK & ngân hàng câu hỏi
│   └── static/
│       ├── index.html       # Single Page Application (Giao diện chính)
│       ├── css/
│       │   └── style.css    # Khung kẻ TianZiGe, font chữ Hán, 3D card
│       └── js/
│           └── app.js       # Vue 3 reactive logic & HanziWriter engine
├── data/
│   └── hanzii.db            # Cơ sở dữ liệu SQLite
├── run.bat                  # Script khởi động 1 click cho Windows
└── README.md                # Tài liệu hướng dẫn chi tiết
```

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)
- **Backend:** Python, FastAPI, Uvicorn, SQLite3.
- **Frontend:** Vue 3 (Reactive Composition API), Tailwind CSS, Font Awesome.
- **Chữ Hán & Bút Thuận:** HanziWriter (Thư viện chuẩn quốc tế mô phỏng vector chữ Hán).
- **Phát âm:** Web Speech API (`zh-CN` Mandarin Speech Synthesis).
- **Hiệu ứng:** Canvas Confetti.
