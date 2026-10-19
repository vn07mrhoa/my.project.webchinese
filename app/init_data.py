import json
import re
import sys
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from app.database import get_connection, init_db

import unicodedata

def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
    return cleaned.replace('ü', 'v').replace('Ü', 'V').lower()

WORDS_DATA = [
    # HSK 1
    {
        "simplified": "你",
        "traditional": "你",
        "pinyin": "nǐ",
        "hanviet": "nhĩ",
        "meaning": "Bạn, anh, chị, em (đại từ nhân xưng ngôi thứ 2)",
        "hsk_level": 1,
        "radical": "亻 (Nhân đứng)",
        "stroke_count": 7,
        "part_of_speech": "Đại từ",
        "examples": [
            {"zh": "你好！", "pinyin": "Nǐ hǎo!", "vi": "Chào bạn!"},
            {"zh": "你是哪国人？", "pinyin": "Nǐ shì nǎ guó rén?", "vi": "Bạn là người nước nào?"}
        ]
    },
    {
        "simplified": "好",
        "traditional": "好",
        "pinyin": "hǎo",
        "hanviet": "hảo",
        "meaning": "Tốt, đẹp, hay, được",
        "hsk_level": 1,
        "radical": "女 (Nữ)",
        "stroke_count": 6,
        "part_of_speech": "Tính từ",
        "examples": [
            {"zh": "这个很好。", "pinyin": "Zhège hěn hǎo.", "vi": "Cái này rất tốt."},
            {"zh": "老师好！", "pinyin": "Lǎoshī hǎo!", "vi": "Chào thầy/cô giáo!"}
        ]
    },
    {
        "simplified": "我",
        "traditional": "我",
        "pinyin": "wǒ",
        "hanviet": "ngã",
        "meaning": "Tôi, tao, tớ, mình (ngôi thứ nhất)",
        "hsk_level": 1,
        "radical": "戈 (Qua)",
        "stroke_count": 7,
        "part_of_speech": "Đại từ",
        "examples": [
            {"zh": "我是学生。", "pinyin": "Wǒ shì xuésheng.", "vi": "Tôi là học sinh."},
            {"zh": "我爱中文。", "pinyin": "Wǒ ài Zhōngwén.", "vi": "Tôi yêu tiếng Trung."}
        ]
    },
    {
        "simplified": "爱",
        "traditional": "愛",
        "pinyin": "ài",
        "hanviet": "ái",
        "meaning": "Yêu, yêu thương, thích",
        "hsk_level": 1,
        "radical": "爫 (Trảo)",
        "stroke_count": 10,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "我爱你。", "pinyin": "Wǒ ài nǐ.", "vi": "Tôi yêu bạn / Anh yêu em."},
            {"zh": "他爱喝茶。", "pinyin": "Tā ài hē chá.", "vi": "Anh ấy thích uống trà."}
        ]
    },
    {
        "simplified": "学习",
        "traditional": "學習",
        "pinyin": "xuéxí",
        "hanviet": "học tập",
        "meaning": "Học tập, học hỏi, nghiên cứu",
        "hsk_level": 1,
        "radical": "子 (Tử)",
        "stroke_count": 11,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "我们在学校学习汉语。", "pinyin": "Wǒmen zài xuéxiào xuéxí Hànyǔ.", "vi": "Chúng tôi học tiếng Hán ở trường."},
            {"zh": "努力学习！", "pinyin": "Nǔlì xuéxí!", "vi": "Cố gắng học tập!"}
        ]
    },
    {
        "simplified": "老师",
        "traditional": "老師",
        "pinyin": "lǎoshī",
        "hanviet": "lão sư",
        "meaning": "Giáo viên, thầy giáo, cô giáo",
        "hsk_level": 1,
        "radical": "耂 (Lão)",
        "stroke_count": 12,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "他是我们的汉语老师。", "pinyin": "Tā shì wǒmen de Hànyǔ lǎoshī.", "vi": "Thầy ấy là giáo viên tiếng Hán của chúng tôi."}
        ]
    },
    {
        "simplified": "朋友",
        "traditional": "朋友",
        "pinyin": "péngyou",
        "hanviet": "bằng hữu",
        "meaning": "Bạn bè, bạn hữu",
        "hsk_level": 1,
        "radical": "月 (Nguyệt)",
        "stroke_count": 12,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "我们是好朋友。", "pinyin": "Wǒmen shì hǎo péngyou.", "vi": "Chúng tôi là bạn tốt của nhau."}
        ]
    },
    {
        "simplified": "谢谢",
        "traditional": "謝謝",
        "pinyin": "xièxie",
        "hanviet": "tạ tạ",
        "meaning": "Cảm ơn, cảm tạ",
        "hsk_level": 1,
        "radical": "讠 (Ngôn)",
        "stroke_count": 12,
        "part_of_speech": "Động từ / Thán từ",
        "examples": [
            {"zh": "谢谢你的帮助！", "pinyin": "Xièxie nǐ de bāngzhù!", "vi": "Cảm ơn sự giúp đỡ của bạn!"},
            {"zh": "不客气，谢谢！", "pinyin": "Bú kèqi, xièxie!", "vi": "Không có chi, cảm ơn!"}
        ]
    },
    {
        "simplified": "喝",
        "traditional": "喝",
        "pinyin": "hē",
        "hanviet": "hát",
        "meaning": "Uống (nước, trà, canh)",
        "hsk_level": 1,
        "radical": "口 (Khẩu)",
        "stroke_count": 12,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "你想喝什么？", "pinyin": "Nǐ xiǎng hē shénme?", "vi": "Bạn muốn uống gì?"},
            {"zh": "我想喝水。", "pinyin": "Wǒ xiǎng hē shuǐ.", "vi": "Tôi muốn uống nước."}
        ]
    },
    {
        "simplified": "吃",
        "traditional": "吃",
        "pinyin": "chī",
        "hanviet": "ngật",
        "meaning": "Ăn (cơm, hoa quả, món ăn)",
        "hsk_level": 1,
        "radical": "口 (Khẩu)",
        "stroke_count": 6,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "你吃饭了吗？", "pinyin": "Nǐ chī fàn le ma?", "vi": "Bạn ăn cơm chưa?"},
            {"zh": "中国菜很好吃。", "pinyin": "Zhōngguó cài hěn hǎochī.", "vi": "Món ăn Trung Quốc rất ngon."}
        ]
    },
    {
        "simplified": "水",
        "traditional": "水",
        "pinyin": "shuǐ",
        "hanviet": "thủy",
        "meaning": "Nước, chất lỏng",
        "hsk_level": 1,
        "radical": "水 (Thủy)",
        "stroke_count": 4,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "请给我一杯水。", "pinyin": "Qǐng gěi wǒ yì bēi shuǐ.", "vi": "Xin cho tôi một cốc nước."}
        ]
    },
    {
        "simplified": "家",
        "traditional": "家",
        "pinyin": "jiā",
        "hanviet": "gia",
        "meaning": "Nhà, gia đình",
        "hsk_level": 1,
        "radical": "宀 (Miên)",
        "stroke_count": 10,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "我家有四口人。", "pinyin": "Wǒ jiā yǒu sì kǒu rén.", "vi": "Gia đình tôi có bốn người."},
            {"zh": "我想回家。", "pinyin": "Wǒ xiǎng huí jiā.", "vi": "Tôi muốn về nhà."}
        ]
    },
    {
        "simplified": "看",
        "traditional": "看",
        "pinyin": "kàn",
        "hanviet": "khán",
        "meaning": "Nhìn, xem, ngắm, đọc (sách)",
        "hsk_level": 1,
        "radical": "目 (Mục)",
        "stroke_count": 9,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "他在看书。", "pinyin": "Tā zài kàn shū.", "vi": "Anh ấy đang đọc sách."},
            {"zh": "你看看这个。", "pinyin": "Nǐ kànkan zhège.", "vi": "Bạn xem cái này xem."}
        ]
    },
    {
        "simplified": "书",
        "traditional": "書",
        "pinyin": "shū",
        "hanviet": "thư",
        "meaning": "Sách, quyển sách",
        "hsk_level": 1,
        "radical": "乛 (Ất)",
        "stroke_count": 4,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "这是一本好书。", "pinyin": "Zhè shì yì běn hǎo shū.", "vi": "Đây là một cuốn sách hay."}
        ]
    },
    {
        "simplified": "去",
        "traditional": "去",
        "pinyin": "qù",
        "hanviet": "khứ",
        "meaning": "Đi, tới, đến",
        "hsk_level": 1,
        "radical": "厶 (Khư)",
        "stroke_count": 5,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "你去哪儿？", "pinyin": "Nǐ qù nǎr?", "vi": "Bạn đi đâu đấy?"},
            {"zh": "我去学校。", "pinyin": "Wǒ qù xuéxiào.", "vi": "Tôi đi đến trường."}
        ]
    },
    
    # HSK 2
    {
        "simplified": "时间",
        "traditional": "時間",
        "pinyin": "shíjiān",
        "hanviet": "thời gian",
        "meaning": "Thời gian, thì giờ",
        "hsk_level": 2,
        "radical": "日 (Nhật)",
        "stroke_count": 14,
        "part_of_speech": "Danh từ",
        "examples": [
            {"zh": "你明天有时间吗？", "pinyin": "Nǐ míngtiān yǒu shíjiān ma?", "vi": "Ngày mai bạn có thời gian không?"}
        ]
    },
    {
        "simplified": "跑步",
        "traditional": "跑步",
        "pinyin": "pǎobù",
        "hanviet": "bào bộ",
        "meaning": "Chạy bộ, chạy",
        "hsk_level": 2,
        "radical": "足 (Túc)",
        "stroke_count": 19,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "我每天早上跑步。", "pinyin": "Wǒ měitiān zǎoshang pǎobù.", "vi": "Mỗi sáng tôi đều chạy bộ."}
        ]
    },
    {
        "simplified": "准备",
        "traditional": "準備",
        "pinyin": "zhǔnbèi",
        "hanviet": "chuẩn bị",
        "meaning": "Chuẩn bị, dự định",
        "hsk_level": 2,
        "radical": "冫 (Băng)",
        "stroke_count": 18,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "你准备好了吗？", "pinyin": "Nǐ zhǔnbèi hǎo le ma?", "vi": "Bạn đã chuẩn bị xong chưa?"}
        ]
    },
    {
        "simplified": "运动",
        "traditional": "運動",
        "pinyin": "yùndòng",
        "hanviet": "vận động",
        "meaning": "Thể thao, vận động",
        "hsk_level": 2,
        "radical": "辶 (Sước)",
        "stroke_count": 16,
        "part_of_speech": "Danh từ / Động từ",
        "examples": [
            {"zh": "多运动对身体好。", "pinyin": "Duō yùndòng duì shēntǐ hǎo.", "vi": "Vận động nhiều rất tốt cho sức khỏe."}
        ]
    },
    {
        "simplified": "欢迎",
        "traditional": "歡迎",
        "pinyin": "huānyíng",
        "hanviet": "hoan nghênh",
        "meaning": "Chào mừng, hoan nghênh",
        "hsk_level": 2,
        "radical": "欠 (Khiếm)",
        "stroke_count": 13,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "欢迎你们来到北京！", "pinyin": "Huānyíng nǐmen lái dào Běijīng!", "vi": "Chào mừng các bạn đến Bắc Kinh!"}
        ]
    },
    {
        "simplified": "懂",
        "traditional": "懂",
        "pinyin": "dǒng",
        "hanviet": "đổng",
        "meaning": "Hiểu, biết rõ",
        "hsk_level": 2,
        "radical": "忄 (Tâm đứng)",
        "stroke_count": 15,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "你听懂了吗？", "pinyin": "Nǐ tīng dǒng le ma?", "vi": "Bạn nghe có hiểu không?"},
            {"zh": "我懂你的意思。", "pinyin": "Wǒ dǒng nǐ de yìsi.", "vi": "Tôi hiểu ý của bạn."}
        ]
    },

    # HSK 3
    {
        "simplified": "打算",
        "traditional": "打算",
        "pinyin": "dǎsuàn",
        "hanviet": "đả toán",
        "meaning": "Dự định, tính toán, lên kế hoạch",
        "hsk_level": 3,
        "radical": "扌 (Thủ)",
        "stroke_count": 19,
        "part_of_speech": "Động từ / Danh từ",
        "examples": [
            {"zh": "周末你有什么打算？", "pinyin": "Zhōumò nǐ yǒu shénme dǎsuàn?", "vi": "Cuối tuần bạn có dự định gì?"}
        ]
    },
    {
        "simplified": "满意",
        "traditional": "滿意",
        "pinyin": "mǎnyì",
        "hanviet": "mãn ý",
        "meaning": "Hài lòng, vừa ý, thỏa mãn",
        "hsk_level": 3,
        "radical": "氵 (Chấm thủy)",
        "stroke_count": 21,
        "part_of_speech": "Tính từ",
        "examples": [
            {"zh": "经理对这个结果很满意。", "pinyin": "Jīnglǐ duì zhège jiéguǒ hěn mǎnyì.", "vi": "Giám đốc rất hài lòng với kết quả này."}
        ]
    },
    {
        "simplified": "健康",
        "traditional": "健康",
        "pinyin": "jiànkāng",
        "hanviet": "kiện khang",
        "meaning": "Khỏe mạnh, sức khỏe",
        "hsk_level": 3,
        "radical": "亻 (Nhân đứng)",
        "stroke_count": 22,
        "part_of_speech": "Tính từ / Danh từ",
        "examples": [
            {"zh": "祝你身体健康！", "pinyin": "Zhù nǐ shēntǐ jiànkāng!", "vi": "Chúc bạn sức khỏe dồi dào!"}
        ]
    },
    {
        "simplified": "解决",
        "traditional": "解決",
        "pinyin": "jiějué",
        "hanviet": "giải quyết",
        "meaning": "Giải quyết, xử lý (vấn đề, khó khăn)",
        "hsk_level": 3,
        "radical": "角 (Giác)",
        "stroke_count": 19,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "问题已经解决了。", "pinyin": "Wèntí yǐjīng jiějué le.", "vi": "Vấn đề đã được giải quyết rồi."}
        ]
    },

    # HSK 4 - 6
    {
        "simplified": "坚持",
        "traditional": "堅持",
        "pinyin": "jiānchí",
        "hanviet": "kiên trì",
        "meaning": "Kiên trì, giữ vững",
        "hsk_level": 4,
        "radical": "土 (Thổ)",
        "stroke_count": 18,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "只要坚持，就会成功。", "pinyin": "Zhǐyào jiānchí, jiù huì chénggōng.", "vi": "Chỉ cần kiên trì, nhất định sẽ thành công."}
        ]
    },
    {
        "simplified": "成功",
        "traditional": "成功",
        "pinyin": "chénggōng",
        "hanviet": "thành công",
        "meaning": "Thành công, thắng lợi",
        "hsk_level": 4,
        "radical": "戈 (Qua)",
        "stroke_count": 11,
        "part_of_speech": "Động từ / Danh từ",
        "examples": [
            {"zh": "祝你面试成功！", "pinyin": "Zhù nǐ miànshì chénggōng!", "vi": "Chúc bạn phỏng vấn thành công!"}
        ]
    },
    {
        "simplified": "珍惜",
        "traditional": "珍惜",
        "pinyin": "zhēnxī",
        "hanviet": "trân tích",
        "meaning": "Trân trọng, quý trọng, nâng niu",
        "hsk_level": 5,
        "radical": "王 (Ngọc)",
        "stroke_count": 22,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "我们应该珍惜时间。", "pinyin": "Wǒmen yīnggāi zhēnxī shíjiān.", "vi": "Chúng ta nên trân trọng thời gian."}
        ]
    },
    {
        "simplified": "领悟",
        "traditional": "領悟",
        "pinyin": "lǐngwù",
        "hanviet": "lĩnh ngộ",
        "meaning": "Lĩnh ngộ, hiểu thấu, cảm nhận sâu sắc",
        "hsk_level": 6,
        "radical": "页 (Hiệt)",
        "stroke_count": 21,
        "part_of_speech": "Động từ",
        "examples": [
            {"zh": "他终于领悟到了人生的哲理。", "pinyin": "Tā zhōngyú lǐngwù dào le rénshēng de zhélǐ.", "vi": "Cuối cùng anh ấy cũng lĩnh ngộ được triết lý nhân sinh."}
        ]
    }
]

QUIZZES_DATA = [
    # HSK 1 - Quizzes
    {
        "level": 1,
        "type": "meaning",
        "question": "Từ \"学习\" có nghĩa là gì?",
        "target_word": "学习",
        "pinyin_hint": "xuéxí",
        "options": ["Học tập", "Nghỉ ngơi", "Đi dạo", "Làm việc"],
        "correct_index": 0,
        "explanation": "学习 (xuéxí - Hán Việt: học tập) có nghĩa là học hành, nghiên cứu, học tập kiến thức."
    },
    {
        "level": 1,
        "type": "pinyin",
        "question": "Phiên âm Pinyin đúng của chữ \"老师\" là gì?",
        "target_word": "老师",
        "pinyin_hint": "",
        "options": ["lǎoshī", "lǎoxī", "làoshī", "láoshī"],
        "correct_index": 0,
        "explanation": "老师 đọc là lǎoshī (lão sư), mang nghĩa là thầy cô giáo."
    },
    {
        "level": 1,
        "type": "hanzi",
        "question": "Chữ Hán nào có nghĩa là \"Bạn bè\"?",
        "target_word": "péngyou",
        "pinyin_hint": "péngyou",
        "options": ["朋友", "老师", "学生", "家人"],
        "correct_index": 0,
        "explanation": "朋友 (péngyou - bằng hữu) có nghĩa là bạn bè."
    },
    {
        "level": 1,
        "type": "listening",
        "question": "Nghe phát âm và chọn chữ Hán chính xác:",
        "target_word": "喝",
        "pinyin_hint": "hē",
        "options": ["吃 (chī)", "喝 (hē)", "看 (kàn)", "去 (qù)"],
        "correct_index": 1,
        "explanation": "喝 (hē) có nghĩa là uống (uống nước, trà)."
    },
    {
        "level": 1,
        "type": "meaning",
        "question": "Câu \"谢谢你的帮助\" có nghĩa là gì?",
        "target_word": "谢谢",
        "pinyin_hint": "xièxie nǐ de bāngzhù",
        "options": ["Cảm ơn sự giúp đỡ của bạn", "Xin lỗi vì đã làm phiền", "Bạn có khỏe không?", "Hẹn gặp lại ngày mai"],
        "correct_index": 0,
        "explanation": "谢谢 (xièxie): cảm ơn, 你的帮助 (nǐ de bāngzhù): sự giúp đỡ của bạn."
    },
    {
        "level": 1,
        "type": "hanzi",
        "question": "Chọn chữ Hán có bộ \"Thủy\" (水) mang nghĩa là \"Nước\":",
        "target_word": "shuǐ",
        "pinyin_hint": "shuǐ",
        "options": ["火", "水", "木", "土"],
        "correct_index": 1,
        "explanation": "水 (shuǐ - âm Hán Việt: Thủy) chỉ nước."
    },

    # HSK 2 - Quizzes
    {
        "level": 2,
        "type": "meaning",
        "question": "Từ \"准备\" có nghĩa là gì?",
        "target_word": "准备",
        "pinyin_hint": "zhǔnbèi",
        "options": ["Chuẩn bị", "Bắt đầu", "Kết thúc", "Nhanh chóng"],
        "correct_index": 0,
        "explanation": "准备 (zhǔnbèi - chuẩn bị) nghĩa là sẵn sàng hoặc dự bị cho việc gì đó."
    },
    {
        "level": 2,
        "type": "pinyin",
        "question": "Chọn Pinyin chuẩn của \"时间\":",
        "target_word": "时间",
        "pinyin_hint": "",
        "options": ["shíjiān", "shíjiāng", "sījiān", "zhíjiān"],
        "correct_index": 0,
        "explanation": "时间 phiên âm là shíjiān (thời gian)."
    },
    {
        "level": 2,
        "type": "hanzi",
        "question": "Từ nào chỉ hoạt động \"Chạy bộ\"?",
        "target_word": "pǎobù",
        "pinyin_hint": "pǎobù",
        "options": ["跑步", "游泳", "打球", "跳舞"],
        "correct_index": 0,
        "explanation": "跑步 (pǎobù - bào bộ) là hành động chạy bộ rèn luyện sức khỏe."
    },
    {
        "level": 2,
        "type": "meaning",
        "question": "\"你听懂了吗？\" được dịch sang tiếng Việt là gì?",
        "target_word": "懂",
        "pinyin_hint": "nǐ tīng dǒng le ma?",
        "options": ["Bạn nghe hiểu chưa?", "Bạn đang nghe gì thế?", "Bạn có thích nghe không?", "Ai đang nói thế?"],
        "correct_index": 0,
        "explanation": "听 (nghe) + 懂 (hiểu) = 听懂 (nghe hiểu)."
    },

    # HSK 3 - Quizzes
    {
        "level": 3,
        "type": "meaning",
        "question": "Từ \"打算\" thường được dùng với nghĩa nào?",
        "target_word": "打算",
        "pinyin_hint": "dǎsuàn",
        "options": ["Dự định / Dự kiến", "Tính toán tiền bạc", "Đánh nhau", "Rời đi"],
        "correct_index": 0,
        "explanation": "打算 (dǎsuàn - đả toán) thường dùng để nói về kế hoạch hay dự định trong tương lai."
    },
    {
        "level": 3,
        "type": "hanzi",
        "question": "Từ nào đồng nghĩa với \"Hài lòng, vừa ý\"?",
        "target_word": "mǎnyì",
        "pinyin_hint": "mǎnyì",
        "options": ["满意", "高兴", "难过", "生气"],
        "correct_index": 0,
        "explanation": "满意 (mǎnyì - mãn ý) mang nghĩa cảm thấy toại nguyện, hài lòng."
    },
    {
        "level": 3,
        "type": "meaning",
        "question": "\"问题已经解决了\" có nghĩa là gì?",
        "target_word": "解决",
        "pinyin_hint": "wèntí yǐjīng jiějué le",
        "options": ["Vấn đề đã được giải quyết rồi", "Vấn đề vẫn còn phức tạp", "Chưa giải quyết xong", "Không có câu hỏi nào cả"],
        "correct_index": 0,
        "explanation": "问题 (vấn đề) + 已经 (đã) + 解决 (giải quyết)."
    },

    # HSK 4 - 6
    {
        "level": 4,
        "type": "meaning",
        "question": "Thành ngữ / Cụm từ \"坚持到底\" có nghĩa là gì?",
        "target_word": "坚持",
        "pinyin_hint": "jiānchí dào dǐ",
        "options": ["Kiên trì đến cùng", "Dừng lại giữa chừng", "Thất bại thảm hại", "Bắt đầu lại từ đầu"],
        "correct_index": 0,
        "explanation": "坚持 (kiên trì) + 到底 (đến đáy, đến cùng) thể hiện sự nỗ lực không ngừng nghỉ."
    },
    {
        "level": 4,
        "type": "hanzi",
        "question": "Từ nào có nghĩa là \"Thành công\"?",
        "target_word": "chénggōng",
        "pinyin_hint": "chénggōng",
        "options": ["成功", "成就", "成倍", "成熟"],
        "correct_index": 0,
        "explanation": "成功 (chénggōng - thành công) là đạt được mục tiêu mong muốn."
    }
]

def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Thêm từ vựng
    print("Đang nạp từ vựng...")
    for w in WORDS_DATA:
        clean_pinyin = strip_accents(w["pinyin"])
        cursor.execute("""
        INSERT OR REPLACE INTO words 
        (simplified, traditional, pinyin, pinyin_clean, hanviet, meaning, hsk_level, radical, stroke_count, part_of_speech, examples)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            w["simplified"],
            w.get("traditional", w["simplified"]),
            w["pinyin"],
            clean_pinyin,
            w["hanviet"],
            w["meaning"],
            w["hsk_level"],
            w.get("radical", ""),
            w.get("stroke_count", 0),
            w.get("part_of_speech", ""),
            json.dumps(w.get("examples", []), ensure_ascii=False)
        ))

    # Tự động nạp vào Notebook và Flashcard 5 từ đầu tiên làm mẫu
    cursor.execute("SELECT id FROM words LIMIT 5")
    initial_words = cursor.fetchall()
    for row in initial_words:
        w_id = row[0]
        cursor.execute("INSERT OR IGNORE INTO notebook (word_id, custom_note) VALUES (?, ?)", (w_id, "Từ vựng trọng tâm cần nhớ"))
        cursor.execute("INSERT OR IGNORE INTO flashcards (word_id, status) VALUES (?, 'new')", (w_id,))

    # Thêm câu hỏi bài tập Quiz
    print("Đang nạp câu hỏi trắc nghiệm...")
    cursor.execute("DELETE FROM quizzes") # Reset quiz bank
    for q in QUIZZES_DATA:
        cursor.execute("""
        INSERT INTO quizzes (level, type, question, target_word, pinyin_hint, options, correct_index, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["level"],
            q["type"],
            q["question"],
            q.get("target_word", ""),
            q.get("pinyin_hint", ""),
            json.dumps(q["options"], ensure_ascii=False),
            q["correct_index"],
            q.get("explanation", "")
        ))

    conn.commit()
    conn.close()
    print("Cơ sở dữ liệu Hanzii đã được khởi tạo hoàn tất!")

if __name__ == "__main__":
    seed_database()
