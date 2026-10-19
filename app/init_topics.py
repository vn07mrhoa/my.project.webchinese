import json
import sys
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from app.database import get_connection, init_db

TOPICS_DATA = [
    # BÀI 1
    {
        "order_num": 1,
        "title": "Bài 1: Chào hỏi (问候)",
        "category": "Giao tiếp cơ bản",
        "description": "Làm quen với các cách chào hỏi thông dụng hàng ngày, xưng hô lịch sự, cách cảm ơn, xin lỗi và làm quen.",
        "level": 1,
        "is_locked": 0,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "你", "pinyin": "nǐ", "hanviet": "nhĩ", "meaning": "Bạn, anh, chị (ngôi thứ 2 số ít)", "example": "你好！(Chào bạn!)", "is_frequent": True},
            {"simplified": "好", "pinyin": "hǎo", "hanviet": "hảo", "meaning": "Tốt, đẹp, hay, khỏe", "example": "我很好。(Tôi rất khỏe.)", "is_frequent": True},
            {"simplified": "您", "pinyin": "nín", "hanviet": "nâm", "meaning": "Ngài, ông, bà (kính ngữ trang trọng của 你)", "example": "老师，您好！(Em chào thầy/cô ạ!)", "is_frequent": True},
            {"simplified": "对不起", "pinyin": "duìbuqǐ", "hanviet": "đối bất khởi", "meaning": "Xin lỗi", "example": "对不起，我来晚了。(Xin lỗi, tôi đến muộn.)", "is_frequent": True},
            {"simplified": "没关系", "pinyin": "méi guānxi", "hanviet": "một quan hệ", "meaning": "Không sao, không có gì", "example": "没关系，请坐！(Không sao, mời ngồi!)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "你们", "pinyin": "nǐmen", "hanviet": "nhĩ môn", "meaning": "Các bạn, các anh chị (ngôi thứ 2 số nhiều)", "example": "你们好！(Chào các bạn!)", "is_frequent": False},
            {"simplified": "老师", "pinyin": "lǎoshī", "hanviet": "lão sư", "meaning": "Thầy giáo, cô giáo", "example": "他是汉语老师。(Thầy ấy là giáo viên tiếng Trung.)", "is_frequent": False},
            {"simplified": "同学", "pinyin": "tóngxué", "hanviet": "đồng học", "meaning": "Bạn học, bạn cùng lớp", "example": "同学们好！(Chào các bạn học sinh!)", "is_frequent": False},
            {"simplified": "请", "pinyin": "qǐng", "hanviet": "thỉnh", "meaning": "Mời, xin, làm ơn", "example": "请进，请坐！(Mời vào, mời ngồi!)", "is_frequent": False},
            {"simplified": "早", "pinyin": "zǎo", "hanviet": "tảo", "meaning": "Sớm, buổi sáng (chào buổi sáng)", "example": "早上好！/ 老师早！(Chào buổi sáng / Chào thầy buổi sáng!)", "is_frequent": False},
            {"simplified": "再见", "pinyin": "zàijiàn", "hanviet": "tái kiến", "meaning": "Tạm biệt, hẹn gặp lại", "example": "明天见，再见！(Mai gặp lại, tạm biệt!)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "你好！", "pinyin": "Nǐ hǎo!", "vi": "Chào bạn!"},
            {"speaker": "B", "zh": "你好！认识你很高兴。", "pinyin": "Nǐ hǎo! Rènshi nǐ hěn gāoxìng.", "vi": "Chào bạn! Rất vui được quen bạn."},
            {"speaker": "A", "zh": "李老师，您好！", "pinyin": "Lǐ lǎoshī, nín hǎo!", "vi": "Em chào thầy Lý ạ!"},
            {"speaker": "B", "zh": "你好，同学们好！请坐。", "pinyin": "Nǐ hǎo, tóngxuémen hǎo! Qǐng zuò.", "vi": "Chào em, chào các em học sinh! Mời các em ngồi."},
            {"speaker": "A", "zh": "对不起，老师，我迟到了。", "pinyin": "Duìbuqǐ, lǎoshī, wǒ chídào le.", "vi": "Xin lỗi thầy, em đến muộn ạ."},
            {"speaker": "B", "zh": "没关系，快请进！", "pinyin": "Méi guānxi, kuài qǐng jìn!", "vi": "Không sao đâu, mau vào lớp đi em!"},
            {"speaker": "A", "zh": "老师再见！同学们再见！", "pinyin": "Lǎoshī zàijiàn! Tóngxuémen zàijiàn!", "vi": "Em chào thầy ạ! Chào tạm biệt các bạn!"},
            {"speaker": "B", "zh": "明天见！", "pinyin": "Míngtiān jiàn!", "vi": "Ngày mai gặp lại nhé!"}
        ],
        "grammar": [
            {
                "title": "1. Công thức chào hỏi cơ bản: [Danh xưng] + 好",
                "explanation": "Trong tiếng Trung, để chào bất kỳ ai một cách thân thiện, bạn ghép danh xưng hoặc tên của người đó với chữ '好' (hǎo).",
                "example": "你好 (Chào bạn) • 您好 (Chào ngài/bác) • 老师好 (Chào thầy cô) • 大家/同学们好 (Chào mọi người/các bạn học)"
            },
            {
                "title": "2. Phân biệt 你 (nǐ) và 您 (nín)",
                "explanation": "'你' dùng cho bạn bè, người ngang hàng hoặc nhỏ tuổi hơn. '您' (chữ 你 có bộ Tâm 心 ở dưới) dùng để thể hiện sự tôn kính với người lớn tuổi, thầy cô, cấp trên hoặc khách hàng.",
                "example": "您好，老师！ (Chào thầy/cô ạ - kính trọng) vs 你好，小王！ (Chào Tiểu Vương - bạn bè)"
            },
            {
                "title": "3. Cặp thoại xin lỗi: 对不起 — 没关系",
                "explanation": "Khi xin lỗi người khác dùng '对不起' (duìbuqǐ). Đối phương đáp lại bằng '没关系' (méi guānxi) có nghĩa là 'không sao, không có chi'.",
                "example": "A: 对不起！ (Xin lỗi!) -> B: 没关系。 (Không sao đâu.)"
            }
        ],
        "quizzes": [
            {
                "question": "Khi gặp thầy giáo vào buổi sáng, câu chào lịch sự và đúng nhất là gì?",
                "options": ["老师，您好！", "你好，老师！", "对不起，老师！", "老师，再见！"],
                "correct_index": 0,
                "explanation": "Với thầy cô giáo, dùng kính ngữ '您' trong '老师，您好！' để thể hiện sự kính trọng cao nhất."
            },
            {
                "question": "Khi vô tình va phải người khác và nói \"对不起！\", người kia sẽ lịch sự đáp lại bằng câu nào?",
                "options": ["没关系", "不客气", "不用谢", "很好"],
                "correct_index": 0,
                "explanation": "Đáp lại lời xin lỗi 对不起 (Duìbuqǐ) luôn là 没关系 (Méi guānxi - Không sao đâu)."
            },
            {
                "question": "Từ \"同学\" (tóngxué) mang ý nghĩa gì?",
                "options": ["Bạn học / Bạn cùng lớp", "Thầy giáo", "Bố mẹ", "Bác sĩ"],
                "correct_index": 0,
                "explanation": "同学 (tóngxué - âm Hán Việt: đồng học) có nghĩa là bạn cùng học, bạn học sinh."
            },
            {
                "question": "Cấu trúc lịch sự mời ai đó làm gì dùng từ nào đứng đầu câu?",
                "options": ["请 (qǐng)", "好 (hǎo)", "你 (nǐ)", "见 (jiàn)"],
                "correct_index": 0,
                "explanation": "Chữ 请 (qǐng - thỉnh) đứng trước động từ để tạo câu mời lịch sự, ví dụ: 请进 (Mời vào), 请坐 (Mời ngồi)."
            }
        ]
    },

    # BÀI 2
    {
        "order_num": 2,
        "title": "Bài 2: Bạn có bận không? (你忙吗？)",
        "category": "Giao tiếp cơ bản",
        "description": "Làm quen với câu hỏi nghi vấn với trợ từ 吗, các phó từ chỉ mức độ 很, 太, phó từ phủ định 不 và các thành viên trong gia đình.",
        "level": 1,
        "is_locked": 0,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "忙", "pinyin": "máng", "hanviet": "mang", "meaning": "Bận, bận rộn", "example": "你忙吗？(Bạn có bận không?)", "is_frequent": True},
            {"simplified": "吗", "pinyin": "ma", "hanviet": "ma", "meaning": "Không? (trợ từ nghi vấn cuối câu)", "example": "你好吗？(Bạn khỏe không?)", "is_frequent": True},
            {"simplified": "很", "pinyin": "hěn", "hanviet": "hẩn", "meaning": "Rất (phó từ mức độ)", "example": "我很忙。(Tôi rất bận.)", "is_frequent": True},
            {"simplified": "太", "pinyin": "tài", "hanviet": "thái", "meaning": "Quá, lắm", "example": "太好了！(Tốt quá rồi!)", "is_frequent": True},
            {"simplified": "不", "pinyin": "bù", "hanviet": "bất", "meaning": "Không (phó từ phủ định)", "example": "我不忙。(Tôi không bận.)", "is_frequent": True},
            {"simplified": "都", "pinyin": "dōu", "hanviet": "đô", "meaning": "Đều, tất cả", "example": "我们都很好。(Chúng tôi đều rất khỏe.)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "爸爸", "pinyin": "bàba", "hanviet": "bá bá", "meaning": "Bố, cha, ba", "example": "我爸爸是医生。(Bố tôi là bác sĩ.)", "is_frequent": False},
            {"simplified": "妈妈", "pinyin": "māma", "hanviet": "ma ma", "meaning": "Mẹ, má", "example": "妈妈在家。(Mẹ đang ở nhà.)", "is_frequent": False},
            {"simplified": "哥哥", "pinyin": "gēge", "hanviet": "ca ca", "meaning": "Anh trai", "example": "我哥哥工作很忙。(Anh trai tôi công việc rất bận.)", "is_frequent": False},
            {"simplified": "弟弟", "pinyin": "dìdi", "hanviet": "đệ đệ", "meaning": "Em trai", "example": "弟弟在学校学习。(Em trai học ở trường.)", "is_frequent": False},
            {"simplified": "他们", "pinyin": "tāmen", "hanviet": "tha môn", "meaning": "Họ, bọn họ", "example": "他们都在工作。(Họ đều đang làm việc.)", "is_frequent": False},
            {"simplified": "累", "pinyin": "lèi", "hanviet": "luy", "meaning": "Mệt, mệt mỏi", "example": "今天我很累。(Hôm nay tôi rất mệt.)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "你最近忙吗？", "pinyin": "Nǐ zuìjìn máng ma?", "vi": "Dạo này bạn có bận không?"},
            {"speaker": "B", "zh": "我很忙，你呢？", "pinyin": "Wǒ hěn máng, nǐ ne?", "vi": "Tôi rất bận, còn bạn thì sao?"},
            {"speaker": "A", "zh": "我不太忙。今天累不累？", "pinyin": "Wǒ bú tài máng. Jīntiān lèi bu lèi?", "vi": "Tôi không bận lắm. Hôm nay có mệt không?"},
            {"speaker": "B", "zh": "有一点儿累。你爸爸、妈妈好吗？", "pinyin": "Yǒu yìdiǎnr lèi. Nǐ bàba, māma hǎo ma?", "vi": "Hơi mệt một chút. Bố mẹ bạn có khỏe không?"},
            {"speaker": "A", "zh": "他们身体都很好，谢谢！", "pinyin": "Tāmen shēntǐ dōu hěn hǎo, xièxie!", "vi": "Sức khỏe của họ đều rất tốt, cảm ơn bạn!"},
            {"speaker": "B", "zh": "你哥哥也忙吗？", "pinyin": "Nǐ gēge yě máng ma?", "vi": "Anh trai bạn cũng bận chứ?"},
            {"speaker": "A", "zh": "他工作很多，也很忙。", "pinyin": "Tā gōngzuò hěn duō, yě hěn máng.", "vi": "Anh ấy công việc rất nhiều, cũng rất bận."},
            {"speaker": "B", "zh": "好的，注意身体！", "pinyin": "Hǎo de, zhùyì shēntǐ!", "vi": "Được rồi, giữ gìn sức khỏe nhé!"}
        ],
        "grammar": [
            {
                "title": "1. Câu hỏi nghi vấn với trợ từ '吗' (ma)",
                "explanation": "Cấu trúc câu hỏi Yes/No: [Câu khẳng định] + 吗? Để trả lời, lặp lại vị ngữ khẳng định hoặc thêm '不' để phủ định.",
                "example": "你忙吗？ (Bạn có bận không?) -> 我很忙 (Tôi rất bận) / 我不忙 (Tôi không bận)."
            },
            {
                "title": "2. Quy tắc biến điệu của phó từ phủ định '不' (bù)",
                "explanation": "Bình thường '不' đọc thanh 4 (bù). Khi đứng trước một chữ mang thanh 4 khác, '不' đổi thành thanh 2 (bú).",
                "example": "不忙 (bù máng - thanh 2) nhưng 不太 (bú tài - thanh 4), 不是 (bú shì - thanh 4)."
            },
            {
                "title": "3. Phó từ '都' (dōu - đều, tất cả)",
                "explanation": "'都' đứng trước động từ/tính từ để chỉ toàn bộ chủ ngữ số nhiều phía trước.",
                "example": "我们都很好。 (Chúng tôi đều rất khỏe.) • 他们都不忙。 (Họ đều không bận.)"
            }
        ],
        "quizzes": [
            {
                "question": "Để biến câu \"他很好\" thành câu hỏi \"Anh ấy có khỏe không?\", bạn làm thế nào?",
                "options": ["Thêm chữ \"吗\" vào cuối câu", "Thêm chữ \"不\" vào đầu câu", "Đổi chữ \"好\" thành \"忙\"", "Bỏ chữ \"他\""],
                "correct_index": 0,
                "explanation": "Chỉ cần thêm trợ từ nghi vấn 吗 vào cuối câu trần thuật: 他很好吗？ (Anh ấy có khỏe không?)."
            },
            {
                "question": "Từ \"不太忙\" phát âm chuẩn pinyin như thế nào?",
                "options": ["bú tài máng", "bù tài máng", "bǔ tài máng", "bù tài māng"],
                "correct_index": 0,
                "explanation": "Vì chữ 太 (tài) mang thanh 4 nên chữ 不 phải biến điệu đọc thành thanh 2: bú tài máng."
            },
            {
                "question": "Câu \"他们都很好\" có nghĩa là gì?",
                "options": ["Họ đều rất khỏe / rất tốt", "Họ đều rất bận", "Bố mẹ rất mệt", "Chúng tôi không tốt lắm"],
                "correct_index": 0,
                "explanation": "他们 (bọn họ) + 都 (đều) + 很好 (rất tốt/khỏe)."
            },
            {
                "question": "Từ nào chỉ \"Anh trai\" trong tiếng Trung?",
                "options": ["哥哥 (gēge)", "弟弟 (dìdi)", "爸爸 (bàba)", "老师 (lǎoshī)"],
                "correct_index": 0,
                "explanation": "哥哥 (gēge) là anh trai, 弟弟 (dìdi) là em trai."
            }
        ]
    },

    # BÀI 3
    {
        "order_num": 3,
        "title": "Bài 3: Ngày mai gặp lại (明天见)",
        "category": "Giao tiếp cơ bản",
        "description": "Cách cảm ơn, đáp lại lời cảm ơn, hẹn gặp lại, các mốc thời gian (hôm nay, ngày mai, hôm qua) và các địa điểm quen thuộc.",
        "level": 1,
        "is_locked": 0,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "今天", "pinyin": "jīntiān", "hanviet": "kim thiên", "meaning": "Hôm nay", "example": "今天星期一。(Hôm nay là thứ hai.)", "is_frequent": True},
            {"simplified": "明天", "pinyin": "míngtiān", "hanviet": "minh thiên", "meaning": "Ngày mai", "example": "明天见！(Ngày mai gặp lại!)", "is_frequent": True},
            {"simplified": "谢谢", "pinyin": "xièxie", "hanviet": "tạ tạ", "meaning": "Cảm ơn", "example": "太谢谢你了！(Cảm ơn bạn rất nhiều!)", "is_frequent": True},
            {"simplified": "不客气", "pinyin": "bú kèqi", "hanviet": "bất khách khí", "meaning": "Không có chi, đừng khách sáo", "example": "不客气，这是我应该做的。(Không có chi, đây là việc tôi nên làm.)", "is_frequent": True},
            {"simplified": "再见", "pinyin": "zàijiàn", "hanviet": "tái kiến", "meaning": "Tạm biệt, hẹn gặp lại", "example": "大家再见！(Tạm biệt mọi người!)", "is_frequent": True},
            {"simplified": "去", "pinyin": "qù", "hanviet": "khứ", "meaning": "Đi, tới", "example": "你去哪儿？(Bạn đi đâu?)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "昨天", "pinyin": "zuótiān", "hanviet": "tạc thiên", "meaning": "Hôm qua", "example": "昨天我很忙。(Hôm qua tôi rất bận.)", "is_frequent": False},
            {"simplified": "见", "pinyin": "jiàn", "hanviet": "kiến", "meaning": "Gặp, nhìn thấy", "example": "一会儿见！(Lát nữa gặp nhé!)", "is_frequent": False},
            {"simplified": "学校", "pinyin": "xuéxiào", "hanviet": "học hiệu", "meaning": "Trường học", "example": "我去学校学习。(Tôi đến trường học tập.)", "is_frequent": False},
            {"simplified": "邮局", "pinyin": "yóujú", "hanviet": "bưu cục", "meaning": "Bưu điện", "example": "邮局远不远？(Bưu điện có xa không?)", "is_frequent": False},
            {"simplified": "寄", "pinyin": "jì", "hanviet": "ký", "meaning": "Gửi (thư, hàng, bưu phẩm)", "example": "我去寄信。(Tôi đi gửi thư.)", "is_frequent": False},
            {"simplified": "信", "pinyin": "xìn", "hanviet": "tín", "meaning": "Thư từ, thư tín", "example": "写信 (Viết thư)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "谢谢你的帮助！", "pinyin": "Xièxie nǐ de bāngzhù!", "vi": "Cảm ơn sự giúp đỡ của bạn!"},
            {"speaker": "B", "zh": "不客气！大家都是好朋友。", "pinyin": "Bú kèqi! Dàjiā dōu shì hǎo péngyou.", "vi": "Không có chi đâu! Mọi người đều là bạn tốt của nhau mà."},
            {"speaker": "A", "zh": "今天下午你去哪儿？", "pinyin": "Jīntiān xiàwǔ nǐ qù nǎr?", "vi": "Chiều nay bạn đi đâu đấy?"},
            {"speaker": "B", "zh": "我去邮局寄信，你去不去？", "pinyin": "Wǒ qù yóujú jì xìn, nǐ qù bu qù?", "vi": "Tôi ra bưu điện gửi thư, bạn đi không?"},
            {"speaker": "A", "zh": "我不去，我要去学校看书。", "pinyin": "Wǒ bú qù, wǒ yào qù xuéxiào kàn shū.", "vi": "Tôi không đi, tôi phải đến trường đọc sách."},
            {"speaker": "B", "zh": "好的，那明天见！", "pinyin": "Hǎo de, nà míngtiān jiàn!", "vi": "Được rồi, thế ngày mai gặp lại nhé!"},
            {"speaker": "A", "zh": "明天见！路上小心！", "pinyin": "Míngtiān jiàn! Lùshang xiǎoxīn!", "vi": "Ngày mai gặp nhé! Đi đường cẩn thận!"},
            {"speaker": "B", "zh": "再见！", "pinyin": "Zàijiàn!", "vi": "Tạm biệt!"}
        ],
        "grammar": [
            {
                "title": "1. Mẫu câu hẹn gặp: [Mốc thời gian / Địa điểm] + 见",
                "explanation": "Để hẹn gặp ai vào một thời điểm hoặc tại địa điểm nào, chỉ cần ghép mốc đó với chữ '见' (jiàn).",
                "example": "明天见 (Mai gặp) • 星期一见 (Thứ hai gặp nhé) • 学校见 (Gặp ở trường nhé)"
            },
            {
                "title": "2. Cấu trúc câu liên động: 去 + [Nơi chốn] + [Hành động]",
                "explanation": "Dùng để diễn đạt hành động 'đi đến đâu để làm gì'.",
                "example": "我去邮局寄信。(Tôi đến bưu điện gửi thư.) • 我去学校看书。(Tôi đến trường đọc sách.)"
            },
            {
                "title": "3. Cặp câu cảm ơn & đáp lại lịch sự",
                "explanation": "Khi ai đó cảm ơn bằng '谢谢' (hoặc 多谢), người lịch sự sẽ đáp lại bằng '不客气' (Bú kèqi - Đừng khách khí) hoặc '不用谢' (Búyòng xiè - Không cần cảm ơn).",
                "example": "A: 谢谢你！ -> B: 不客气！"
            }
        ],
        "quizzes": [
            {
                "question": "Đáp lại lời cảm ơn \"谢谢！\", câu nào sau đây là tự nhiên và chính xác nhất?",
                "options": ["不客气", "没关系", "再见", "对不起"],
                "correct_index": 0,
                "explanation": "Cảm ơn 谢谢 đi đôi với 不客气 (Bú kèqi - Không có chi, đừng khách sáo)."
            },
            {
                "question": "Câu \"我去学校看书\" diễn đạt ý nghĩa gì?",
                "options": ["Tôi đến trường đọc sách", "Tôi ở nhà đọc sách", "Tôi đi bưu điện gửi sách", "Trường học có rất nhiều sách"],
                "correct_index": 0,
                "explanation": "去 (đi) + 学校 (trường học) + 看书 (đọc sách) = đi trường đọc sách."
            },
            {
                "question": "Từ chỉ \"Hôm qua\" trong tiếng Trung là gì?",
                "options": ["昨天 (zuótiān)", "今天 (jīntiān)", "明天 (míngtiān)", "每天 (měitiān)"],
                "correct_index": 0,
                "explanation": "昨天 (zuótiān) là hôm qua, 今天 (jīntiān) là hôm nay, 明天 (míngtiān) là ngày mai."
            },
            {
                "question": "Khi muốn nói \"Gặp lại vào thứ Hai nhé!\", bạn nói câu nào?",
                "options": ["星期一见！", "星期二见！", "明天见！", "昨天见！"],
                "correct_index": 0,
                "explanation": "星期一 (Thứ Hai) + 见 (Gặp) = 星期一见 (Thứ Hai gặp lại nhé!)."
            }
        ]
    },

    # BÀI 4
    {
        "order_num": 4,
        "title": "Bài 4: Ngày, Tháng, Năm (日期与时间)",
        "category": "Thời gian & Lịch trình",
        "description": "Nắm vững quy tắc nói năm, tháng, ngày, thứ trong tuần, xem giờ phút theo thứ tự từ lớn đến nhỏ của tư duy tiếng Trung.",
        "level": 1,
        "is_locked": 1,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "年", "pinyin": "nián", "hanviet": "niên", "meaning": "Năm", "example": "今年是2026年。(Năm nay là năm 2026.)", "is_frequent": True},
            {"simplified": "月", "pinyin": "yuè", "hanviet": "nguyệt", "meaning": "Tháng, mặt trăng", "example": "十月 (Tháng 10)", "is_frequent": True},
            {"simplified": "号", "pinyin": "hào", "hanviet": "hiệu", "meaning": "Ngày (dùng trong văn nói)", "example": "今天15号。(Hôm nay ngày 15.)", "is_frequent": True},
            {"simplified": "星期", "pinyin": "xīngqī", "hanviet": "tinh kỳ", "meaning": "Tuần, thứ", "example": "星期天 (Chủ nhật)", "is_frequent": True},
            {"simplified": "几", "pinyin": "jǐ", "hanviet": "kỷ", "meaning": "Mấy (hỏi số lượng < 10)", "example": "今天星期几？(Hôm nay thứ mấy?)", "is_frequent": True},
            {"simplified": "现在", "pinyin": "xiànzài", "hanviet": "hiện tại", "meaning": "Bây giờ, hiện tại", "example": "现在几点？(Bây giờ mấy giờ rồi?)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "日", "pinyin": "rì", "hanviet": "nhật", "meaning": "Ngày, mặt trời (dùng trong văn viết)", "example": "10月13日 (Ngày 13 tháng 10)", "is_frequent": False},
            {"simplified": "点", "pinyin": "diǎn", "hanviet": "điểm", "meaning": "Giờ (đơn vị giờ)", "example": "八点 (8 giờ)", "is_frequent": False},
            {"simplified": "分", "pinyin": "fēn", "hanviet": "phân", "meaning": "Phút", "example": "八点十分 (8 giờ 10 phút)", "is_frequent": False},
            {"simplified": "半", "pinyin": "bàn", "hanviet": "bán", "meaning": "Nửa, rưỡi (30 phút)", "example": "九点半 (9 rưỡi / 9 giờ 30)", "is_frequent": False},
            {"simplified": "生日", "pinyin": "shēngrì", "hanviet": "sinh nhật", "meaning": "Sinh nhật", "example": "祝你生日快乐！(Chúc bạn sinh nhật vui vẻ!)", "is_frequent": False},
            {"simplified": "什么时候", "pinyin": "shénme shíhou", "hanviet": "thập ma thời hậu", "meaning": "Khi nào, lúc nào", "example": "你什么时候来？(Khi nào bạn đến?)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "请问，今天几月几号？", "pinyin": "Qǐngwèn, jīntiān jǐ yuè jǐ hào?", "vi": "Xin hỏi, hôm nay là ngày mấy tháng mấy?"},
            {"speaker": "B", "zh": "今天10月13号，星期二。", "pinyin": "Jīntiān shí yuè shísān hào, xīngqī'èr.", "vi": "Hôm nay là ngày 13 tháng 10, thứ Ba."},
            {"speaker": "A", "zh": "现在几点了？", "pinyin": "Xiànzài jǐ diǎn le?", "vi": "Bây giờ là mấy giờ rồi?"},
            {"speaker": "B", "zh": "现在上午九点半。", "pinyin": "Xiànzài shàngwǔ jiǔ diǎn bàn.", "vi": "Bây giờ là 9 giờ rưỡi sáng."},
            {"speaker": "A", "zh": "你的生日是几月几号？", "pinyin": "Nǐ de shēngrì shì jǐ yuè jǐ hào?", "vi": "Sinh nhật của bạn là ngày mấy tháng mấy?"},
            {"speaker": "B", "zh": "我的生日是11月20号，你呢？", "pinyin": "Wǒ de shēngrì shì shíyī yuè èrshí hào, nǐ ne?", "vi": "Sinh nhật tôi là ngày 20 tháng 11, còn bạn?"},
            {"speaker": "A", "zh": "下个星期日是我的生日！", "pinyin": "Xià gè xīngqīrì shì wǒ de shēngrì!", "vi": "Chủ nhật tuần sau là sinh nhật của tôi đấy!"},
            {"speaker": "B", "zh": "太好了，提前祝你生日快乐！", "pinyin": "Tài hǎo le, tíqián zhù nǐ shēngrì kuàilè!", "vi": "Tuyệt quá, chúc mừng sinh nhật bạn trước nhé!"}
        ],
        "grammar": [
            {
                "title": "1. Quy tắc thời gian: Từ lớn đến bé (Năm -> Tháng -> Ngày -> Giờ)",
                "explanation": "Người Trung Quốc tư duy từ cái bao quát đến cái chi tiết: [Năm] -> [Tháng] -> [Ngày] -> [Buổi] -> [Giờ] -> [Phút].",
                "example": "2026年10月13日 上午9点30分 (9 giờ 30 phút sáng ngày 13/10/2026)"
            },
            {
                "title": "2. Cách gọi các thứ trong tuần",
                "explanation": "Bắt đầu bằng '星期' (xīngqī) cộng với các số từ 1 đến 6. Riêng Chủ Nhật dùng '星期天' hoặc '星期日'.",
                "example": "星期一 (Thứ Hai) • 星期二 (Thứ Ba) • ... • 星期六 (Thứ Bảy) • 星期天 (Chủ Nhật)"
            },
            {
                "title": "3. Mẫu câu hỏi giờ: 现在几点？ (Xiànzài jǐ diǎn?)",
                "explanation": "Công thức trả lời giờ: [Số] + 点 (diǎn) + [Số] + 分 (fēn). Nếu giờ rưỡi dùng 半 (bàn).",
                "example": "十点 (10 giờ) • 三点半 (3 giờ rưỡi) • 七点十五分 (7 giờ 15 phút)"
            }
        ],
        "quizzes": [
            {
                "question": "Thứ Ba trong tiếng Trung được gọi là gì?",
                "options": ["星期二", "星期三", "星期一", "星期天"],
                "correct_index": 0,
                "explanation": "Trong tiếng Trung, thứ tính từ số 1 (一 là Thứ Hai), do đó Thứ Ba là 星期二 (Xīngqī'èr)."
            },
            {
                "question": "Giờ \"9 giờ 30 phút\" có thể diễn đạt bằng cách nào ngắn gọn nhất?",
                "options": ["九点半 (jiǔ diǎn bàn)", "九点三十分", "九点分", "半九点"],
                "correct_index": 0,
                "explanation": "九点半 (jiǔ diǎn bàn) là cách nói 9 rưỡi / 9 giờ 30 thông dụng nhất trong khẩu ngữ."
            },
            {
                "question": "Khi muốn hỏi \"Hôm nay ngày mấy tháng mấy?\", bạn hỏi như thế nào?",
                "options": ["今天几月几号？", "今天几号几月？", "现在几点了？", "今天星期几？"],
                "correct_index": 0,
                "explanation": "Theo quy tắc lớn trước nhỏ sau: Tháng trước ngày sau -> 几月几号？ (Mấy tháng mấy ngày?)."
            },
            {
                "question": "Chủ Nhật trong tiếng Trung có thể nói bằng 2 từ nào?",
                "options": ["星期天 / 星期日", "星期七 / 星期八", "星期六 / 星期天", "星期日 / 星期一"],
                "correct_index": 0,
                "explanation": "Chủ nhật không dùng 星期七 mà dùng 星期天 (khẩu ngữ) hoặc 星期日 (văn viết)."
            }
        ]
    },

    # BÀI 5
    {
        "order_num": 5,
        "title": "Bài 5: Bạn đi đâu đấy? (你去哪儿？)",
        "category": "Giao thông & Địa điểm",
        "description": "Cách hỏi và chỉ phương hướng, vị trí, địa điểm: trường học, thư viện, ngân hàng, bưu điện, về nhà, rút tiền.",
        "level": 1,
        "is_locked": 1,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "去", "pinyin": "qù", "hanviet": "khứ", "meaning": "Đi, tới", "example": "你去哪儿？(Bạn đi đâu?)", "is_frequent": True},
            {"simplified": "哪儿", "pinyin": "nǎr", "hanviet": "na nhi", "meaning": "Ở đâu, đâu", "example": "你在哪儿？(Bạn ở đâu?)", "is_frequent": True},
            {"simplified": "学校", "pinyin": "xuéxiào", "hanviet": "học hiệu", "meaning": "Trường học", "example": "这是我们的学校。(Đây là trường học của chúng tôi.)", "is_frequent": True},
            {"simplified": "回", "pinyin": "huí", "hanviet": "hồi", "meaning": "Về, trở về", "example": "回家 (Về nhà)", "is_frequent": True},
            {"simplified": "家", "pinyin": "jiā", "hanviet": "gia", "meaning": "Nhà, gia đình", "example": "我想家。(Tôi nhớ nhà.)", "is_frequent": True},
            {"simplified": "看书", "pinyin": "kàn shū", "hanviet": "khán thư", "meaning": "Đọc sách", "example": "他在图书馆看书。(Anh ấy đọc sách ở thư viện.)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "图书馆", "pinyin": "túshūguǎn", "hanviet": "đồ thư quán", "meaning": "Thư viện", "example": "去图书馆借书。(Đến thư viện mượn sách.)", "is_frequent": False},
            {"simplified": "银行", "pinyin": "yínháng", "hanviet": "ngân hàng", "meaning": "Ngân hàng", "example": "中国银行 (Ngân hàng Trung Quốc)", "is_frequent": False},
            {"simplified": "取钱", "pinyin": "qǔ qián", "hanviet": "thủ tiền", "meaning": "Rút tiền", "example": "我去银行取钱。(Tôi đến ngân hàng rút tiền.)", "is_frequent": False},
            {"simplified": "宿舍", "pinyin": "sùshè", "hanviet": "túc xá", "meaning": "Ký túc xá", "example": "回宿舍休息。(Về ký túc xá nghỉ ngơi.)", "is_frequent": False},
            {"simplified": "找", "pinyin": "zhǎo", "hanviet": "trảo", "meaning": "Tìm, kiếm", "example": "我找李老师。(Tôi tìm thầy Lý.)", "is_frequent": False},
            {"simplified": "朋友", "pinyin": "péngyou", "hanviet": "bằng hữu", "meaning": "Bạn bè", "example": "找朋友聊天。(Tìm bạn bè nói chuyện.)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "小王，你去哪儿？", "pinyin": "Xiǎo Wáng, nǐ qù nǎr?", "vi": "Tiểu Vương, bạn đi đâu đấy?"},
            {"speaker": "B", "zh": "我去图书馆看书，你呢？", "pinyin": "Wǒ qù túshūguǎn kàn shū, nǐ ne?", "vi": "Tôi đến thư viện đọc sách, còn bạn thì sao?"},
            {"speaker": "A", "zh": "我不去图书馆，我去银行取钱。", "pinyin": "Wǒ bú qù túshūguǎn, wǒ qù yínháng qǔ qián.", "vi": "Tôi không đến thư viện, tôi đến ngân hàng rút tiền."},
            {"speaker": "B", "zh": "银行远不远？", "pinyin": "Yínháng yuǎn bu yuǎn?", "vi": "Ngân hàng có xa không?"},
            {"speaker": "A", "zh": "不太远，就在学校旁边。", "pinyin": "Bú tài yuǎn, jiù zài xuéxiào pángbiān.", "vi": "Không xa lắm, ở ngay bên cạnh trường học thôi."},
            {"speaker": "B", "zh": "取完钱你回宿舍吗？", "pinyin": "Qǔ wán qián nǐ huí sùshè ma?", "vi": "Rút tiền xong bạn có về ký túc xá không?"},
            {"speaker": "A", "zh": "我不回宿舍，我回家看爸爸妈妈。", "pinyin": "Wǒ bù huí sùshè, wǒ huí jiā kàn bàba māma.", "vi": "Tôi không về ký túc xá, tôi về nhà thăm bố mẹ."},
            {"speaker": "B", "zh": "好的，祝你周末愉快！", "pinyin": "Hǎo de, zhù nǐ zhōumò yúkuài!", "vi": "Được rồi, chúc bạn cuối tuần vui vẻ!"}
        ],
        "grammar": [
            {
                "title": "1. Mẫu câu hỏi địa điểm: [Chủ ngữ] + 去哪儿？",
                "explanation": "'哪儿' (nǎr) là đại từ nghi vấn chỉ nơi chốn, tương đương 'ở đâu / đâu' trong tiếng Việt.",
                "example": "你去哪儿？ (Bạn đi đâu?) -> 我去银行。 (Tôi đến ngân hàng.)"
            },
            {
                "title": "2. Phân biệt 去 (đi) và 回 (về)",
                "explanation": "'去' dùng khi di chuyển đến một địa điểm thông thường. '回' mang nghĩa quay trở về nơi xuất phát, nơi chốn quen thuộc của mình như nhà (回家), ký túc xá (回宿舍), tổ quốc (回国).",
                "example": "我去学校 (Tôi đến trường) vs 我回家 (Tôi về nhà - không nói 我去家)."
            }
        ],
        "quizzes": [
            {
                "question": "Từ nào dùng để nói \"Về nhà\" một cách chính xác nhất?",
                "options": ["回家 (huí jiā)", "去家 (qù jiā)", "来家 (lái jiā)", "看家 (kàn jiā)"],
                "correct_index": 0,
                "explanation": "Trong tiếng Trung, trở về nhà dùng động từ 回 (huí): 回家 (huí jiā)."
            },
            {
                "question": "Cụm từ \"去银行取钱\" có nghĩa là gì?",
                "options": ["Đến ngân hàng rút tiền", "Đến thư viện đọc sách", "Đến trường học tập", "Về nhà lấy tiền"],
                "correct_index": 0,
                "explanation": "银行 (ngân hàng) + 取钱 (rút tiền) = Đến ngân hàng rút tiền."
            },
            {
                "question": "Đại từ nghi vấn nào dùng để hỏi \"Ở đâu / đi đâu\"?",
                "options": ["哪儿 (nǎr)", "什么 (shénme)", "谁 (shéi)", "几 (jǐ)"],
                "correct_index": 0,
                "explanation": "哪儿 (nǎr) mang nghĩa là 'ở đâu, đi đâu'."
            },
            {
                "question": "Từ \"图书馆\" (túshūguǎn) mang ý nghĩa gì?",
                "options": ["Thư viện", "Bưu điện", "Bệnh viện", "Ký túc xá"],
                "correct_index": 0,
                "explanation": "图书馆 (đồ thư quán) chính là thư viện đọc sách."
            }
        ]
    },

    # BÀI 6
    {
        "order_num": 6,
        "title": "Bài 6: Giới thiệu & Hỏi thăm (介绍与认识)",
        "category": "Giao tiếp xã hội",
        "description": "Cách hỏi họ tên, xưng hô lịch sự 'quý tính', giới thiệu quốc tịch (Việt Nam, Trung Quốc), nghề nghiệp và biểu đạt sự vui mừng khi quen biết.",
        "level": 1,
        "is_locked": 1,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "叫", "pinyin": "jiào", "hanviet": "khiếu", "meaning": "Tên là, gọi là", "example": "我叫李明。(Tôi tên là Lý Minh.)", "is_frequent": True},
            {"simplified": "什么", "pinyin": "shénme", "hanviet": "thập ma", "meaning": "Cái gì, gì", "example": "你叫什么名字？(Bạn tên là gì?)", "is_frequent": True},
            {"simplified": "名字", "pinyin": "míngzi", "hanviet": "danh tự", "meaning": "Tên, họ tên", "example": "好听的名字 (Cái tên hay)", "is_frequent": True},
            {"simplified": "认识", "pinyin": "rènshi", "hanviet": "nhận thức", "meaning": "Quen biết, làm quen", "example": "认识你很高兴。(Rất vui được quen bạn.)", "is_frequent": True},
            {"simplified": "高兴", "pinyin": "gāoxìng", "hanviet": "cao hứng", "meaning": "Vui vẻ, hân hoan", "example": "我很高兴。(Tôi rất vui.)", "is_frequent": True},
            {"simplified": "贵姓", "pinyin": "guìxìng", "hanviet": "quý tính", "meaning": "Quý danh, họ (trang trọng)", "example": "请问，您贵姓？(Xin hỏi, ngài họ gì ạ?)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "姓", "pinyin": "xìng", "hanviet": "tính", "meaning": "Họ (danh từ / động từ)", "example": "我姓阮。(Tôi họ Nguyễn.)", "is_frequent": False},
            {"simplified": "是", "pinyin": "shì", "hanviet": "thị", "meaning": "Là (động từ to be)", "example": "我是学生。(Tôi là học sinh.)", "is_frequent": False},
            {"simplified": "哪国人", "pinyin": "nǎ guó rén", "hanviet": "na quốc nhân", "meaning": "Người nước nào", "example": "你是哪国人？(Bạn là người nước nào?)", "is_frequent": False},
            {"simplified": "中国", "pinyin": "Zhōngguó", "hanviet": "Trung Quốc", "meaning": "Nước Trung Quốc", "example": "中国人 (Người Trung Quốc)", "is_frequent": False},
            {"simplified": "越南", "pinyin": "Yuènán", "hanviet": "Việt Nam", "meaning": "Nước Việt Nam", "example": "越南人 (Người Việt Nam)", "is_frequent": False},
            {"simplified": "学生", "pinyin": "xuésheng", "hanviet": "học sinh", "meaning": "Học sinh, sinh viên", "example": "我是留学生。(Tôi là lưu học sinh.)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "请问，您贵姓？", "pinyin": "Qǐngwèn, nín guìxìng?", "vi": "Xin hỏi, ngài mang quý họ gì ạ?"},
            {"speaker": "B", "zh": "免贵，我姓王。你叫什么名字？", "pinyin": "Miǎnguì, wǒ xìng Wáng. Nǐ jiào shénme míngzi?", "vi": "Không dám, tôi họ Vương. Bạn tên là gì?"},
            {"speaker": "A", "zh": "我叫阮文海。认识您很高兴！", "pinyin": "Wǒ jiào Ruǎn Wénhǎi. Rènshi nín hěn gāoxìng!", "vi": "Tôi tên là Nguyễn Văn Hải. Rất vui được quen biết ngài!"},
            {"speaker": "B", "zh": "认识你我也很高兴！你是哪国人？", "pinyin": "Rènshi nǐ wǒ yě hěn gāoxìng! Nǐ shì nǎ guó rén?", "vi": "Quen biết bạn tôi cũng rất vui! Bạn là người nước nào vậy?"},
            {"speaker": "A", "zh": "我是越南人。王老师，您是中国人吗？", "pinyin": "Wǒ shì Yuènán rén. Wáng lǎoshī, nín shì Zhōngguó rén ma?", "vi": "Tôi là người Việt Nam. Thầy Vương, thầy là người Trung Quốc phải không ạ?"},
            {"speaker": "B", "zh": "对，我是北京人，是这里的汉语老师。", "pinyin": "Duì, wǒ shì Běijīng rén, shì zhèlǐ de Hànyǔ lǎoshī.", "vi": "Đúng rồi, tôi là người Bắc Kinh, là giáo viên dạy tiếng Hán ở đây."},
            {"speaker": "A", "zh": "太棒了！我是您的学生。", "pinyin": "Tài bàng le! Wǒ shì nín de xuésheng.", "vi": "Tuyệt quá ạ! Em là học sinh của thầy."},
            {"speaker": "B", "zh": "欢迎你来中国学习！", "pinyin": "Huānyíng nǐ lái Zhōngguó xuéxí!", "vi": "Chào mừng em đến Trung Quốc học tập!"}
        ],
        "grammar": [
            {
                "title": "1. Mẫu câu hỏi tên: 你叫什么名字？ (Nǐ jiào shénme míngzi?)",
                "explanation": "Cách trả lời: 我叫 + [Họ tên]. '叫' đóng vai trò là động từ mang nghĩa 'tên là, gọi là'.",
                "example": "你叫什么名字？ -> 我叫李明。 (Tôi tên là Lý Minh.)"
            },
            {
                "title": "2. Lời hỏi họ trang trọng: 您贵姓？ (Nín guìxìng?)",
                "explanation": "Dùng trong giao tiếp thương mại, xã giao lần đầu gặp người lớn tuổi hoặc đối tác. Người được hỏi thường nhã nhặn trả lời: 免贵，我姓... (Miǎnguì, wǒ xìng...).",
                "example": "A: 请问，您贵姓？ -> B: 免贵，我姓张。"
            },
            {
                "title": "3. Mẫu câu hỏi quốc tịch: 你是哪国人？",
                "explanation": "Công thức trả lời: 我是 + [Tên quốc gia] + 人.",
                "example": "我是越南人。(Tôi là người Việt Nam.) • 我是中国人。(Tôi là người Trung Quốc.)"
            }
        ],
        "quizzes": [
            {
                "question": "Khi muốn hỏi một đối tác trang trọng \"Xin hỏi ngài họ gì?\", câu nói chuẩn mực nhất là gì?",
                "options": ["请问，您贵姓？", "你叫什么？", "你是谁？", "你是哪国人？"],
                "correct_index": 0,
                "explanation": "Kính ngữ hỏi họ lịch sự nhất trong tiếng Trung là: 请问，您贵姓？ (Qǐngwèn, nín guìxìng?)."
            },
            {
                "question": "Đáp lại câu chào \"认识你很高兴！\", câu đối lại thích hợp nhất là gì?",
                "options": ["认识你我也很高兴！", "对不起！", "没关系！", "我是越南人。"],
                "correct_index": 0,
                "explanation": "Thêm phó từ 也 (cũng) để đáp lại sự thiện cảm: 认识你我也很高兴！ (Quen bạn tôi cũng rất vui!)."
            },
            {
                "question": "Từ \"越南人\" trong tiếng Trung phát âm pinyin là gì?",
                "options": ["Yuènán rén", "Zhōngguó rén", "Běijīng rén", "Měiguó rén"],
                "correct_index": 0,
                "explanation": "越南人 phiên âm là Yuènán rén (người Việt Nam)."
            },
            {
                "question": "Đại từ nghi vấn \"什么\" (shénme) mang nghĩa là gì?",
                "options": ["Cái gì / gì", "Ở đâu", "Mấy / bao nhiêu", "Ai"],
                "correct_index": 0,
                "explanation": "什么 (shénme) có nghĩa là 'cái gì, gì'."
            }
        ]
    },

    # BÀI 7
    {
        "order_num": 7,
        "title": "Bài 7: Bạn ăn gì? (你吃什么？)",
        "category": "Ăn uống & Đời sống",
        "description": "Gọi món ăn, đồ uống trong nhà hàng, các món ăn đặc trưng của Trung Quốc: cơm, mì sợi, sủi cảo, bánh bao, bia, trà và các lượng từ thông dụng.",
        "level": 1,
        "is_locked": 0,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "吃", "pinyin": "chī", "hanviet": "ngật", "meaning": "Ăn", "example": "吃饭 (Ăn cơm)", "is_frequent": True},
            {"simplified": "喝", "pinyin": "hē", "hanviet": "hát", "meaning": "Uống", "example": "喝水 (Uống nước)", "is_frequent": True},
            {"simplified": "饭", "pinyin": "fàn", "hanviet": "phạn", "meaning": "Cơm, bữa ăn", "example": "米饭 (Cơm trắng)", "is_frequent": True},
            {"simplified": "面条", "pinyin": "miàntiáo", "hanviet": "diện điều", "meaning": "Mì sợi", "example": "一碗牛肉面 (Một bát mì bò)", "is_frequent": True},
            {"simplified": "包子", "pinyin": "bāozi", "hanviet": "bao tử", "meaning": "Bánh bao", "example": "吃包子 (Ăn bánh bao)", "is_frequent": True},
            {"simplified": "水", "pinyin": "shuǐ", "hanviet": "thủy", "meaning": "Nước", "example": "矿泉水 (Nước khoáng)", "is_frequent": True},
            {"simplified": "要", "pinyin": "yào", "hanviet": "yếu", "meaning": "Muốn, cần, gọi (món)", "example": "我要一碗面条。(Tôi muốn một bát mì.)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "饺子", "pinyin": "jiǎozi", "hanviet": "giảo tử", "meaning": "Sủi cảo, bánh chẻo", "example": "吃饺子 (Ăn sủi cảo)", "is_frequent": False},
            {"simplified": "茶", "pinyin": "chá", "hanviet": "trà", "meaning": "Trà, chè", "example": "绿茶 / 红茶 (Trà xanh / Hồng trà)", "is_frequent": False},
            {"simplified": "啤酒", "pinyin": "píjiǔ", "hanviet": "tỳ tửu", "meaning": "Bia", "example": "青岛啤酒 (Bia Thanh Đảo)", "is_frequent": False},
            {"simplified": "碗", "pinyin": "wǎn", "hanviet": "oản", "meaning": "Bát, chén (lượng từ)", "example": "两碗米饭 (Hai bát cơm)", "is_frequent": False},
            {"simplified": "杯", "pinyin": "bēi", "hanviet": "bôi", "meaning": "Cốc, ly (lượng từ)", "example": "一杯水 (Một cốc nước)", "is_frequent": False},
            {"simplified": "好吃", "pinyin": "hǎochī", "hanviet": "hảo ngật", "meaning": "Ngon (đồ ăn)", "example": "中国菜很好吃。(Món Trung rất ngon.)", "is_frequent": False},
            {"simplified": "想", "pinyin": "xiǎng", "hanviet": "tưởng", "meaning": "Nghĩ, muốn, nhớ", "example": "我想吃包子。(Tôi muốn ăn bánh bao.)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "中午到了，你想吃什么？", "pinyin": "Zhōngwǔ dào le, nǐ xiǎng chī shénme?", "vi": "Đến trưa rồi, bạn muốn ăn gì nào?"},
            {"speaker": "B", "zh": "我想去学校食堂吃包子和饺子。你呢？", "pinyin": "Wǒ xiǎng qù xuéxiào shítáng chī bāozi hé jiǎozi. Nǐ ne?", "vi": "Tôi muốn đến nhà ăn trường ăn bánh bao và sủi cảo. Còn bạn?"},
            {"speaker": "A", "zh": "我想吃牛肉面条。服务员，点菜！", "pinyin": "Wǒ xiǎng chī niúròu miàntiáo. Fúwùyuán, diǎncài!", "vi": "Tôi muốn ăn mì thịt bò. Phục vụ ơi, gọi món!"},
            {"speaker": "B", "zh": "服务员，我们要一碗面条，十个饺子。", "pinyin": "Fúwùyuán, wǒmen yào yì wǎn miàntiáo, shí gè jiǎozi.", "vi": "Phục vụ ơi, cho chúng tôi một bát mì và mười cái sủi cảo."},
            {"speaker": "A", "zh": "你们想喝点儿什么？", "pinyin": "Nǐmen xiǎng hē diǎnr shénme?", "vi": "Các bạn muốn uống chút gì không?"},
            {"speaker": "B", "zh": "请给我一杯热茶，给他一瓶啤酒。", "pinyin": "Qǐng gěi wǒ yì bēi rè chá, gěi tā yì píng píjiǔ.", "vi": "Cho tôi một ly trà nóng, còn cho anh ấy một chai bia nhé."},
            {"speaker": "A", "zh": "这里的菜好吃吗？", "pinyin": "Zhèlǐ de cài hǎochī ma?", "vi": "Món ăn ở đây có ngon không?"},
            {"speaker": "B", "zh": "菜很好吃，价格也很便宜！", "pinyin": "Cài hěn hǎochī, jiàgé yě hěn piányi!", "vi": "Đồ ăn rất ngon, giá cả cũng rất rẻ nữa!"}
        ],
        "grammar": [
            {
                "title": "1. Mẫu câu gọi đồ ăn thức uống: 我要 / 我想 + [Món ăn / Đồ uống]",
                "explanation": "'要' (yào) biểu thị yêu cầu gọi món dứt khoát. '想' (xiǎng) biểu thị mong muốn, nguyện vọng.",
                "example": "我要一碗面条。 (Tôi muốn một bát mì.) • 我想喝茶。 (Tôi muốn uống trà.)"
            },
            {
                "title": "2. Sử dụng lượng từ chỉ đồ ăn: 碗 (bát), 杯 (cốc), 瓶 (chai), 个 (cái)",
                "explanation": "Trong tiếng Trung, danh từ luôn đi kèm lượng từ thích hợp: [Số từ] + [Lượng từ] + [Danh từ].",
                "example": "一碗米饭 (Một bát cơm) • 两杯茶 (Hai ly trà) • 四个包子 (Bốn cái bánh bao)"
            },
            {
                "title": "3. Cặp tính từ khen đồ ăn: 好吃 (hǎochī) và 好喝 (hǎohē)",
                "explanation": "Đồ ăn ngon dùng '好吃'. Đồ uống ngon dùng '好喝'.",
                "example": "饺子很好吃！ (Sủi cảo ngon quá!) • 这个啤酒很好喝！ (Bia này uống ngon thật!)"
            }
        ],
        "quizzes": [
            {
                "question": "Để nói \"Cho tôi một ly nước\", bạn nói câu nào chuẩn nhất?",
                "options": ["请给我一杯水", "请给我一碗水", "请给我一个水", "请给我一水"],
                "correct_index": 0,
                "explanation": "Lượng từ của nước rót vào ly/cốc là 杯 (bēi): 一杯水 (Yì bēi shuǐ)."
            },
            {
                "question": "Đồ uống \"Bia\" trong tiếng Trung là gì?",
                "options": ["啤酒 (píjiǔ)", "绿茶 (lǜchá)", "矿泉水 (kuàngquánshuǐ)", "牛奶 (niúnǎi)"],
                "correct_index": 0,
                "explanation": "啤酒 (píjiǔ - âm Hán Việt: tỳ tửu) chính là bia."
            },
            {
                "question": "Khi khen một món canh hoặc loại trà thơm ngon, ta dùng từ nào?",
                "options": ["好喝 (hǎohē)", "好吃 (hǎochī)", "好看 (hǎokàn)", "好听 (hǎotīng)"],
                "correct_index": 0,
                "explanation": "Đồ uống ngon dùng 好喝 (hǎohē), còn đồ ăn ngon dùng 好吃 (hǎochī)."
            },
            {
                "question": "Câu \"你想吃什么？\" có nghĩa là gì?",
                "options": ["Bạn muốn ăn gì?", "Bạn muốn uống gì?", "Bạn đi đâu ăn cơm?", "Món này có ngon không?"],
                "correct_index": 0,
                "explanation": "想 (muốn) + 吃 (ăn) + 什么 (gì) = Bạn muốn ăn gì?"
            }
        ]
    },

    # BÀI 8
    {
        "order_num": 8,
        "title": "Bài 8: Mua sắm & Giá cả (买东西)",
        "category": "Mua sắm & Tiền tệ",
        "description": "Cách hỏi giá cả, các đơn vị tiền tệ Trung Quốc (Đồng/Tệ/Hào), đơn vị cân lạng, kỹ năng mặc cả và thanh toán khi đi siêu thị, mua hoa quả.",
        "level": 1,
        "is_locked": 0,
        "vocabularies": [
            # Từ trọng tâm thường dùng
            {"simplified": "买", "pinyin": "mǎi", "hanviet": "mãi", "meaning": "Mua", "example": "我想买东西。(Tôi muốn mua đồ.)", "is_frequent": True},
            {"simplified": "多少", "pinyin": "duōshao", "hanviet": "đa thiểu", "meaning": "Bao nhiêu", "example": "多少钱？(Bao nhiêu tiền?)", "is_frequent": True},
            {"simplified": "钱", "pinyin": "qián", "hanviet": "tiền", "meaning": "Tiền bạc, tiền", "example": "钱包 (Ví tiền)", "is_frequent": True},
            {"simplified": "块", "pinyin": "kuài", "hanviet": "khối", "meaning": "Đồng, tệ (văn nói của 元)", "example": "五块钱 (5 đồng / 5 tệ)", "is_frequent": True},
            {"simplified": "太贵了", "pinyin": "tài guì le", "hanviet": "thái quý liễu", "meaning": "Đắt quá, đắt quá rồi", "example": "太贵了，便宜点儿吧！(Đắt quá, bớt chút đi!)", "is_frequent": True},
            {"simplified": "便宜", "pinyin": "piányi", "hanviet": "tiện nghi", "meaning": "Rẻ, bớt giá", "example": "便宜一点儿。(Rẻ hơn một chút đi.)", "is_frequent": True},
            {"simplified": "一共", "pinyin": "yígòng", "hanviet": "nhất cộng", "meaning": "Tổng cộng", "example": "一共多少钱？(Tổng cộng bao nhiêu tiền?)", "is_frequent": True},
            # Từ vựng mở rộng trong bài
            {"simplified": "卖", "pinyin": "mài", "hanviet": "mại", "meaning": "Bán", "example": "这个苹果怎么卖？(Táo này bán thế nào?)", "is_frequent": False},
            {"simplified": "斤", "pinyin": "jīn", "hanviet": "cân", "meaning": "Cân Trung Quốc (= 500g)", "example": "一斤苹果 (Một cân táo = nửa ký)", "is_frequent": False},
            {"simplified": "苹果", "pinyin": "píngguǒ", "hanviet": "bình quả", "meaning": "Quả táo", "example": "红苹果 (Táo đỏ)", "is_frequent": False},
            {"simplified": "香蕉", "pinyin": "xiāngjiāo", "hanviet": "hương tiêu", "meaning": "Quả chuối", "example": "买两斤香蕉 (Mua 2 cân chuối)", "is_frequent": False},
            {"simplified": "毛", "pinyin": "máo", "hanviet": "mao", "meaning": "Hào (1 tệ = 10 hào)", "example": "三块五毛 (3 tệ 5 hào)", "is_frequent": False},
            {"simplified": "还要", "pinyin": "hái yào", "hanviet": "hoàn yếu", "meaning": "Còn cần, còn lấy gì nữa", "example": "你还要别的吗？(Bạn còn lấy gì khác không?)", "is_frequent": False},
            {"simplified": "找钱", "pinyin": "zhǎo qián", "hanviet": "trảo tiền", "meaning": "Thối tiền thừa, trả lại tiền", "example": "找你五块。(Thối lại cho bạn 5 tệ.)", "is_frequent": False}
        ],
        "dialogues": [
            {"speaker": "A", "zh": "你好，老板，苹果多少钱一斤？", "pinyin": "Nǐ hǎo, lǎobǎn, píngguǒ duōshao qián yì jīn?", "vi": "Chào ông chủ, táo bao nhiêu tiền một cân (500g) vậy?"},
            {"speaker": "B", "zh": "红苹果六块钱一斤，很甜很好吃！", "pinyin": "Hóng píngguǒ liù kuài qián yì jīn, hěn tián hěn hǎochī!", "vi": "Táo đỏ 6 đồng một cân, rất ngọt và ngon lắm!"},
            {"speaker": "A", "zh": "六块太贵了！便宜点儿吧，五块行吗？", "pinyin": "Liù kuài tài guì le! Piányi diǎnr ba, wǔ kuài xíng ma?", "vi": "6 đồng đắt quá! Bớt chút đi, 5 đồng được không?"},
            {"speaker": "B", "zh": "你要几斤？买三斤的话，算你五块！", "pinyin": "Nǐ yào jǐ jīn? Mǎi sān jīn dehuà, suàn nǐ wǔ kuài!", "vi": "Bạn lấy mấy cân? Nếu mua 3 cân thì tính bạn 5 đồng!"},
            {"speaker": "A", "zh": "行，我要三斤苹果。香蕉多少钱？", "pinyin": "Xíng, wǒ yào sān jīn píngguǒ. Xiāngjiāo duōshao qián?", "vi": "Được, tôi lấy 3 cân táo. Còn chuối bao nhiêu tiền?"},
            {"speaker": "B", "zh": "香蕉四块钱一斤，也要两斤吗？", "pinyin": "Xiāngjiāo sì kuài qián yì jīn, yě yào liǎng jīn ma?", "vi": "Chuối 4 đồng một cân, bạn cũng lấy 2 cân chứ?"},
            {"speaker": "A", "zh": "好的，来两斤香蕉。一共多少钱？", "pinyin": "Hǎo de, lái liǎng jīn xiāngjiāo. Yígòng duōshao qián?", "vi": "Được, cho 2 cân chuối. Tổng cộng hết bao nhiêu tiền?"},
            {"speaker": "B", "zh": "三斤苹果十五块，两斤香蕉八块，一共二十三块！给你五十，找你二十七块。", "pinyin": "Sān jīn píngguǒ shíwǔ kuài, liǎng jīn xiāngjiāo bā kuài, yígòng èrshísān kuài! Gěi nǐ wǔshí, zhǎo nǐ èrshíqī kuài.", "vi": "3 cân táo 15 đồng, 2 cân chuối 8 đồng, tổng cộng 23 đồng! Nhận bạn 50, trả lại bạn 27 đồng nhé."}
        ],
        "grammar": [
            {
                "title": "1. Mẫu câu hỏi giá kinh điển: [Đồ vật] + 多少钱？",
                "explanation": "Có thể thêm đơn vị lượng từ phía sau để hỏi giá theo đơn vị: [Đồ vật] + 多少钱 + [Đơn vị: 一斤 / 一个 / 一瓶]?",
                "example": "苹果多少钱一斤？ (Táo bao nhiêu tiền một cân?) • 这件衣服多少钱？ (Bộ quần áo này bao nhiêu tiền?)"
            },
            {
                "title": "2. Khẩu ngữ mặc cả: 太贵了，便宜点儿吧！",
                "explanation": "Cụm từ cửa miệng khi đi mua sắm ở Trung Quốc: '太贵了' (Tài guì le - Đắt quá) kết hợp '便宜点儿吧' (Piányi diǎnr ba - Bớt chút đi mà).",
                "example": "太贵了，能不能便宜点儿？ (Đắt quá, có thể giảm giá chút không?)"
            },
            {
                "title": "3. Đơn vị đo lường 斤 (jīn) của Trung Quốc",
                "explanation": "Lưu ý cực kỳ quan trọng: 1 斤 (cân) của Trung Quốc chỉ bằng 500 gram (nửa kilogram). Muốn mua 1kg Việt Nam thì phải nói là '两斤' (liǎng jīn) hoặc '一公斤' (yì gōngjīn).",
                "example": "一斤 = 500g • 两斤 = 1kg • 一公斤 = 1kg"
            }
        ],
        "quizzes": [
            {
                "question": "1 斤 (cân) trong đơn vị tính của Trung Quốc bằng bao nhiêu gram?",
                "options": ["500 gram (nửa kg)", "1000 gram (1 kg)", "2000 gram (2 kg)", "100 gram"],
                "correct_index": 0,
                "explanation": "1 斤 (jīn) của Trung Quốc bằng đúng 500 gram (0.5 kg). 1 kg chuẩn quốc tế gọi là 一公斤 (yì gōngjīn)."
            },
            {
                "question": "Câu cửa miệng người mua hàng hay dùng để mặc cả giảm giá là gì?",
                "options": ["太贵了，便宜点儿吧！", "太好了，我都要！", "不用找钱了！", "多少钱一斤？"],
                "correct_index": 0,
                "explanation": "太贵了，便宜点儿吧！ (Đắt quá, rẻ một chút đi!) là câu mặc cả quen thuộc nhất."
            },
            {
                "question": "Từ \"一共\" (yígòng) trong câu \"一共多少钱？\" có nghĩa là gì?",
                "options": ["Tổng cộng", "Đơn giá", "Tiền thối", "Giảm giá"],
                "correct_index": 0,
                "explanation": "一共 (yígòng - âm Hán Việt: nhất cộng) có nghĩa là tổng cộng tất cả."
            },
            {
                "question": "Đơn vị tiền tệ thường dùng nhất trong khẩu ngữ giao tiếp hàng ngày ở Trung Quốc là gì?",
                "options": ["块 (kuài)", "元 (yuán)", "分 (fēn)", "盾 (dùn)"],
                "correct_index": 0,
                "explanation": "Trong văn nói, người Trung Quốc gần như luôn dùng chữ 块 (kuài) thay cho 元 (yuán), ví dụ: 5 tệ -> 五块 (wǔ kuài)."
            }
        ]
    }
]

def seed_topics():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics")
    
    for t in TOPICS_DATA:
        cursor.execute("""
        INSERT INTO topics (title, category, description, level, vocabularies, dialogues, grammar, quizzes, is_locked, order_num)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["title"],
            t["category"],
            t["description"],
            t["level"],
            json.dumps(t["vocabularies"], ensure_ascii=False),
            json.dumps(t["dialogues"], ensure_ascii=False),
            json.dumps(t["grammar"], ensure_ascii=False),
            json.dumps(t["quizzes"], ensure_ascii=False),
            t["is_locked"],
            t["order_num"]
        ))
    
    conn.commit()
    conn.close()
    print("Đã nạp thành công 8 bài học mở rộng với đầy đủ từ trọng tâm, từ mở rộng, hội thoại và bài tập!")

if __name__ == "__main__":
    seed_topics()
