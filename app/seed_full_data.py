import json
import unicodedata
import sys
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from app.database import get_connection, init_db

def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
    return cleaned.replace('ü', 'v').replace('Ü', 'V').lower()

# DANH SÁCH TỪ VỰNG MỞ RỘNG (HƠN 70 TỪ VỰNG HSK 1 - 4)
EXPANDED_WORDS = [
    # Nhóm 1: Đại từ & Xưng hô
    {"simplified": "你", "traditional": "你", "pinyin": "nǐ", "hanviet": "nhĩ", "meaning": "Bạn, anh, chị (ngôi 2)", "hsk": 1, "radical": "亻 (Nhân đứng)", "strokes": 7, "pos": "Đại từ", "examples": [{"zh": "你好！", "pinyin": "Nǐ hǎo!", "vi": "Chào bạn!"}]},
    {"simplified": "我", "traditional": "我", "pinyin": "wǒ", "hanviet": "ngã", "meaning": "Tôi, tao, tớ (ngôi 1)", "hsk": 1, "radical": "戈 (Qua)", "strokes": 7, "pos": "Đại từ", "examples": [{"zh": "我是学生。", "pinyin": "Wǒ shì xuésheng.", "vi": "Tôi là học sinh."}]},
    {"simplified": "他", "traditional": "他", "pinyin": "tā", "hanviet": "tha", "meaning": "Anh ấy, cậu ấy (ngôi 3 nam)", "hsk": 1, "radical": "亻 (Nhân đứng)", "strokes": 5, "pos": "Đại từ", "examples": [{"zh": "他是医生。", "pinyin": "Tā shì yīshēng.", "vi": "Anh ấy là bác sĩ."}]},
    {"simplified": "她", "traditional": "她", "pinyin": "tā", "hanviet": "tha", "meaning": "Cô ấy, bà ấy (ngôi 3 nữ)", "hsk": 1, "radical": "女 (Nữ)", "strokes": 6, "pos": "Đại từ", "examples": [{"zh": "她很漂亮。", "pinyin": "Tā hěn piàoliang.", "vi": "Cô ấy rất xinh đẹp."}]},
    {"simplified": "我们", "traditional": "我們", "pinyin": "wǒmen", "hanviet": "ngã môn", "meaning": "Chúng tôi, chúng ta", "hsk": 1, "radical": "亻 (Nhân đứng)", "strokes": 12, "pos": "Đại từ", "examples": [{"zh": "我们都是朋友。", "pinyin": "Wǒmen dōu shì péngyou.", "vi": "Chúng tôi đều là bạn bè."}]},
    {"simplified": "他们", "traditional": "他們", "pinyin": "tāmen", "hanviet": "tha môn", "meaning": "Họ, bọn họ", "hsk": 1, "radical": "亻 (Nhân đứng)", "strokes": 10, "pos": "Đại từ", "examples": [{"zh": "他们去看电影了。", "pinyin": "Tāmen qù kàn diànyǐng le.", "vi": "Họ đi xem phim rồi."}]},
    {"simplified": "您", "traditional": "您", "pinyin": "nín", "hanviet": "nâm", "meaning": "Ngài, ông, bà (kính ngữ)", "hsk": 2, "radical": "心 (Tâm)", "strokes": 11, "pos": "Đại từ", "examples": [{"zh": "老师，您好！", "pinyin": "Lǎoshī, nín hǎo!", "vi": "Em chào thầy ạ!"}]},
    {"simplified": "谁", "traditional": "誰", "pinyin": "shéi", "hanviet": "thùy", "meaning": "Ai, người nào", "hsk": 1, "radical": "讠 (Ngôn)", "strokes": 10, "pos": "Đại từ nghi vấn", "examples": [{"zh": "他是谁？", "pinyin": "Tā shì shéi?", "vi": "Anh ấy là ai?"}]},
    {"simplified": "什么", "traditional": "什麼", "pinyin": "shénme", "hanviet": "thập ma", "meaning": "Cái gì, gì", "hsk": 1, "radical": "亻 (Nhân đứng)", "strokes": 7, "pos": "Đại từ nghi vấn", "examples": [{"zh": "这是什么？", "pinyin": "Zhè shì shénme?", "vi": "Đây là cái gì?"}]},
    {"simplified": "哪儿", "traditional": "哪兒", "pinyin": "nǎr", "hanviet": "na nhi", "meaning": "Ở đâu, nơi nào", "hsk": 1, "radical": "口 (Khẩu)", "strokes": 11, "pos": "Đại từ nghi vấn", "examples": [{"zh": "你去哪儿？", "pinyin": "Nǐ qù nǎr?", "vi": "Bạn đi đâu?"}]},

    # Nhóm 2: Con người, Nghề nghiệp & Gia đình
    {"simplified": "老师", "traditional": "老師", "pinyin": "lǎoshī", "hanviet": "lão sư", "meaning": "Thầy giáo, cô giáo", "hsk": 1, "radical": "耂 (Lão)", "strokes": 12, "pos": "Danh từ", "examples": [{"zh": "王老师教汉语。", "pinyin": "Wáng lǎoshī jiāo Hànyǔ.", "vi": "Thầy Vương dạy tiếng Hán."}]},
    {"simplified": "学生", "traditional": "學生", "pinyin": "xuésheng", "hanviet": "học sinh", "meaning": "Học sinh, sinh viên", "hsk": 1, "radical": "子 (Tử)", "strokes": 13, "pos": "Danh từ", "examples": [{"zh": "他是大学生。", "pinyin": "Tā shì dàxuésheng.", "vi": "Cậu ấy là sinh viên đại học."}]},
    {"simplified": "朋友", "traditional": "朋友", "pinyin": "péngyou", "hanviet": "bằng hữu", "meaning": "Bạn bè", "hsk": 1, "radical": "月 (Nguyệt)", "strokes": 12, "pos": "Danh từ", "examples": [{"zh": "我们是好朋友。", "pinyin": "Wǒmen shì hǎo péngyou.", "vi": "Chúng tôi là bạn tốt."}]},
    {"simplified": "医生", "traditional": "醫生", "pinyin": "yīshēng", "hanviet": "y sinh", "meaning": "Bác sĩ", "hsk": 1, "radical": "匚 (Phương)", "strokes": 12, "pos": "Danh từ", "examples": [{"zh": "他在医院当医生。", "pinyin": "Tā zài yīyuàn dāng yīshēng.", "vi": "Anh ấy làm bác sĩ ở bệnh viện."}]},
    {"simplified": "爸爸", "traditional": "爸爸", "pinyin": "bàba", "hanviet": "bá bá", "meaning": "Bố, cha", "hsk": 1, "radical": "父 (Phụ)", "strokes": 8, "pos": "Danh từ", "examples": [{"zh": "我爸爸身体很好。", "pinyin": "Wǒ bàba shēntǐ hěn hǎo.", "vi": "Bố tôi sức khỏe rất tốt."}]},
    {"simplified": "妈妈", "traditional": "媽媽", "pinyin": "māma", "hanviet": "ma ma", "meaning": "Mẹ, má", "hsk": 1, "radical": "女 (Nữ)", "strokes": 12, "pos": "Danh từ", "examples": [{"zh": "妈妈做的菜很好吃。", "pinyin": "Māma zuò de cài hěn hǎochī.", "vi": "Món mẹ nấu rất ngon."}]},
    {"simplified": "哥哥", "traditional": "哥哥", "pinyin": "gēge", "hanviet": "ca ca", "meaning": "Anh trai", "hsk": 2, "radical": "口 (Khẩu)", "strokes": 10, "pos": "Danh từ", "examples": [{"zh": "我哥哥比我大两岁。", "pinyin": "Wǒ gēge bǐ wǒ dà liǎng suì.", "vi": "Anh trai lớn hơn tôi hai tuổi."}]},
    {"simplified": "姐姐", "traditional": "姐姐", "pinyin": "jiějie", "hanviet": "tỷ tỷ", "meaning": "Chị gái", "hsk": 2, "radical": "女 (Nữ)", "strokes": 8, "pos": "Danh từ", "examples": [{"zh": "我姐姐在银行工作。", "pinyin": "Wǒ jiějie zài yínháng gōngzuò.", "vi": "Chị gái tôi làm việc ở ngân hàng."}]},
    {"simplified": "弟弟", "traditional": "弟弟", "pinyin": "dìdi", "hanviet": "đệ đệ", "meaning": "Em trai", "hsk": 2, "radical": "弓 (Cung)", "strokes": 7, "pos": "Danh từ", "examples": [{"zh": "弟弟喜欢踢足球。", "pinyin": "Dìdi xǐhuan tī zúqiú.", "vi": "Em trai thích đá bóng."}]},
    {"simplified": "妹妹", "traditional": "妹妹", "pinyin": "mèimei", "hanviet": "muội muội", "meaning": "Em gái", "hsk": 2, "radical": "女 (Nữ)", "strokes": 8, "pos": "Danh từ", "examples": [{"zh": "妹妹正在听音乐。", "pinyin": "Mèimei zhèngzài tīng yīnyuè.", "vi": "Em gái đang nghe nhạc."}]},
    {"simplified": "服务员", "traditional": "服務員", "pinyin": "fúwùyuán", "hanviet": "phục vụ viên", "meaning": "Nhân viên phục vụ", "hsk": 2, "radical": "亻 (Nhân)", "strokes": 24, "pos": "Danh từ", "examples": [{"zh": "服务员，请结账！", "pinyin": "Fúwùyuán, qǐng jiézhàng!", "vi": "Phục vụ ơi, tính tiền giúp!"}]},

    # Nhóm 3: Ăn uống & Mua sắm
    {"simplified": "吃", "traditional": "吃", "pinyin": "chī", "hanviet": "ngật", "meaning": "Ăn", "hsk": 1, "radical": "口 (Khẩu)", "strokes": 6, "pos": "Động từ", "examples": [{"zh": "你吃饭了吗？", "pinyin": "Nǐ chī fàn le ma?", "vi": "Bạn ăn cơm chưa?"}]},
    {"simplified": "喝", "traditional": "喝", "pinyin": "hē", "hanviet": "hát", "meaning": "Uống", "hsk": 1, "radical": "口 (Khẩu)", "strokes": 12, "pos": "Động từ", "examples": [{"zh": "我想喝一杯水。", "pinyin": "Wǒ xiǎng hē yì bēi shuǐ.", "vi": "Tôi muốn uống một cốc nước."}]},
    {"simplified": "水", "traditional": "水", "pinyin": "shuǐ", "hanviet": "thủy", "meaning": "Nước", "hsk": 1, "radical": "水 (Thủy)", "strokes": 4, "pos": "Danh từ", "examples": [{"zh": "请喝水。", "pinyin": "Qǐng hē shuǐ.", "vi": "Mời uống nước."}]},
    {"simplified": "茶", "traditional": "茶", "pinyin": "chá", "hanviet": "trà", "meaning": "Trà, chè", "hsk": 1, "radical": "艹 (Thảo)", "strokes": 9, "pos": "Danh từ", "examples": [{"zh": "中国人喜欢喝茶。", "pinyin": "Zhōngguórén xǐhuan hē chá.", "vi": "Người Trung Quốc thích uống trà."}]},
    {"simplified": "米饭", "traditional": "米飯", "pinyin": "mǐfàn", "hanviet": "mễ phạn", "meaning": "Cơm trắng", "hsk": 1, "radical": "米 (Mễ)", "strokes": 13, "pos": "Danh từ", "examples": [{"zh": "我吃米饭。", "pinyin": "Wǒ chī mǐfàn.", "vi": "Tôi ăn cơm trắng."}]},
    {"simplified": "面条", "traditional": "麵條", "pinyin": "miàntiáo", "hanviet": "diện điều", "meaning": "Mì sợi", "hsk": 2, "radical": "面 (Diện)", "strokes": 16, "pos": "Danh từ", "examples": [{"zh": "他要了一碗牛肉面条。", "pinyin": "Tā yào le yì wǎn niúròu miàntiáo.", "vi": "Anh ấy gọi một bát mì bò."}]},
    {"simplified": "包子", "traditional": "包子", "pinyin": "bāozi", "hanviet": "bao tử", "meaning": "Bánh bao", "hsk": 2, "radical": "勹 (Bao)", "strokes": 8, "pos": "Danh từ", "examples": [{"zh": "热腾腾的包子很好吃。", "pinyin": "Rèténgténg de bāozi hěn hǎochī.", "vi": "Bánh bao nóng hổi rất ngon."}]},
    {"simplified": "苹果", "traditional": "蘋果", "pinyin": "píngguǒ", "hanviet": "bình quả", "meaning": "Quả táo", "hsk": 1, "radical": "艹 (Thảo)", "strokes": 16, "pos": "Danh từ", "examples": [{"zh": "苹果六块钱一斤。", "pinyin": "Píngguǒ liù kuài qián yì jīn.", "vi": "Táo sáu tệ một cân."}]},
    {"simplified": "买", "traditional": "買", "pinyin": "mǎi", "hanviet": "mãi", "meaning": "Mua", "hsk": 1, "radical": "乛 (Ất)", "strokes": 6, "pos": "Động từ", "examples": [{"zh": "我想买衣服。", "pinyin": "Wǒ xiǎng mǎi yīfu.", "vi": "Tôi muốn mua quần áo."}]},
    {"simplified": "卖", "traditional": "賣", "pinyin": "mài", "hanviet": "mại", "meaning": "Bán", "hsk": 2, "radical": "十 (Thập)", "strokes": 8, "pos": "Động từ", "examples": [{"zh": "这家店卖水果。", "pinyin": "Zhè jiā diàn mài shuǐguǒ.", "vi": "Cửa hàng này bán hoa quả."}]},
    {"simplified": "钱", "traditional": "錢", "pinyin": "qián", "hanviet": "tiền", "meaning": "Tiền bạc", "hsk": 1, "radical": "钅 (Kim)", "strokes": 10, "pos": "Danh từ", "examples": [{"zh": "这个多少钱？", "pinyin": "Zhège duōshao qián?", "vi": "Cái này bao nhiêu tiền?"}]},
    {"simplified": "块", "traditional": "塊", "pinyin": "kuài", "hanviet": "khối", "meaning": "Đồng, tệ (khẩu ngữ)", "hsk": 1, "radical": "土 (Thổ)", "strokes": 7, "pos": "Lượng từ", "examples": [{"zh": "一共十五块。", "pinyin": "Yígòng shíwǔ kuài.", "vi": "Tổng cộng mười lăm tệ."}]},
    {"simplified": "贵", "traditional": "貴", "pinyin": "guì", "hanviet": "quý", "meaning": "Đắt, quý báu", "hsk": 2, "radical": "贝 (Bối)", "strokes": 9, "pos": "Tính từ", "examples": [{"zh": "太贵了，便宜点儿吧！", "pinyin": "Tài guì le, piányi diǎnr ba!", "vi": "Đắt quá, rẻ chút đi!"}]},
    {"simplified": "便宜", "traditional": "便宜", "pinyin": "piányi", "hanviet": "tiện nghi", "meaning": "Rẻ, giá hời", "hsk": 2, "radical": "亻 (Nhân)", "strokes": 16, "pos": "Tính từ", "examples": [{"zh": "这件衣服很便宜。", "pinyin": "Zhè jiàn yīfu hěn piányi.", "vi": "Bộ quần áo này rất rẻ."}]},

    # Nhóm 4: Hoạt động & Động từ cốt lõi
    {"simplified": "学习", "traditional": "學習", "pinyin": "xuéxí", "hanviet": "học tập", "meaning": "Học tập, học hỏi", "hsk": 1, "radical": "子 (Tử)", "strokes": 11, "pos": "Động từ", "examples": [{"zh": "我们努力学习中文。", "pinyin": "Wǒmen nǔlì xuéxí Zhōngwén.", "vi": "Chúng tôi chăm chỉ học tiếng Trung."}]},
    {"simplified": "工作", "traditional": "工作", "pinyin": "gōngzuò", "hanviet": "công tác", "meaning": "Làm việc, công việc", "hsk": 1, "radical": "亻 (Nhân)", "strokes": 10, "pos": "Động từ / Danh từ", "examples": [{"zh": "他在公司工作。", "pinyin": "Tā zài gōngsī gōngzuò.", "vi": "Anh ấy làm việc ở công ty."}]},
    {"simplified": "看", "traditional": "看", "pinyin": "kàn", "hanviet": "khán", "meaning": "Xem, nhìn, đọc", "hsk": 1, "radical": "目 (Mục)", "strokes": 9, "pos": "Động từ", "examples": [{"zh": "他在看书。", "pinyin": "Tā zài kàn shū.", "vi": "Anh ấy đang đọc sách."}]},
    {"simplified": "听", "traditional": "聽", "pinyin": "tīng", "hanviet": "thính", "meaning": "Nghe", "hsk": 1, "radical": "口 (Khẩu)", "strokes": 7, "pos": "Động từ", "examples": [{"zh": "请大家听我说。", "pinyin": "Qǐng dàjiā tīng wǒ shuō.", "vi": "Xin mọi người nghe tôi nói."}]},
    {"simplified": "说话", "traditional": "說話", "pinyin": "shuōhuà", "hanviet": "thuyết thoại", "meaning": "Nói chuyện, nói năng", "hsk": 1, "radical": "讠 (Ngôn)", "strokes": 17, "pos": "Động từ", "examples": [{"zh": "他们在开心地说话。", "pinyin": "Tāmen zài kāixīn de shuōhuà.", "vi": "Họ đang nói chuyện vui vẻ."}]},
    {"simplified": "写", "traditional": "寫", "pinyin": "xiě", "hanviet": "tả", "meaning": "Viết", "hsk": 1, "radical": "冖 (Mịch)", "strokes": 5, "pos": "Động từ", "examples": [{"zh": "我写汉字。", "pinyin": "Wǒ xiě hànzì.", "vi": "Tôi viết chữ Hán."}]},
    {"simplified": "去", "traditional": "去", "pinyin": "qù", "hanviet": "khứ", "meaning": "Đi, tới", "hsk": 1, "radical": "厶 (Khư)", "strokes": 5, "pos": "Động từ", "examples": [{"zh": "我去学校。", "pinyin": "Wǒ qù xuéxiào.", "vi": "Tôi đến trường."}]},
    {"simplified": "来", "traditional": "來", "pinyin": "lái", "hanviet": "lai", "meaning": "Đến, tới", "hsk": 1, "radical": "木 (Mộc)", "strokes": 7, "pos": "Động từ", "examples": [{"zh": "欢迎你来我家。", "pinyin": "Huānyíng nǐ lái wǒ jiā.", "vi": "Hoan nghênh bạn đến nhà tôi."}]},
    {"simplified": "回", "traditional": "回", "pinyin": "huí", "hanviet": "hồi", "meaning": "Về, trở về", "hsk": 1, "radical": "囗 (Vi)", "strokes": 6, "pos": "Động từ", "examples": [{"zh": "我想回家。", "pinyin": "Wǒ xiǎng huí jiā.", "vi": "Tôi muốn về nhà."}]},
    {"simplified": "做", "traditional": "做", "pinyin": "zuò", "hanviet": "tác", "meaning": "Làm, nấu", "hsk": 1, "radical": "亻 (Nhân)", "strokes": 11, "pos": "Động từ", "examples": [{"zh": "你在做什么？", "pinyin": "Nǐ zài zuò shénme?", "vi": "Bạn đang làm gì thế?"}]},
    {"simplified": "坐", "traditional": "坐", "pinyin": "zuò", "hanviet": "tọa", "meaning": "Ngồi, đi (xe buýt, tàu)", "hsk": 1, "radical": "土 (Thổ)", "strokes": 7, "pos": "Động từ", "examples": [{"zh": "请坐！", "pinyin": "Qǐng zuò!", "vi": "Mời ngồi!"}]},
    {"simplified": "住", "traditional": "住", "pinyin": "zhù", "hanviet": "trú", "meaning": "Ở, sinh sống", "hsk": 1, "radical": "亻 (Nhân)", "strokes": 7, "pos": "Động từ", "examples": [{"zh": "你住在哪里？", "pinyin": "Nǐ zhù zài nǎli?", "vi": "Bạn sống ở đâu?"}]},
    {"simplified": "喜欢", "traditional": "喜歡", "pinyin": "xǐhuan", "hanviet": "hỉ hoan", "meaning": "Thích, yêu thích", "hsk": 1, "radical": "士 (Sĩ)", "strokes": 18, "pos": "Động từ", "examples": [{"zh": "我喜欢喝中国茶。", "pinyin": "Wǒ xǐhuan hē Zhōngguó chá.", "vi": "Tôi thích uống trà Trung Quốc."}]},
    {"simplified": "想", "traditional": "想", "pinyin": "xiǎng", "hanviet": "tưởng", "meaning": "Nghĩ, muốn, nhớ", "hsk": 1, "radical": "心 (Tâm)", "strokes": 13, "pos": "Động từ / Trợ động từ", "examples": [{"zh": "我想去北京旅游。", "pinyin": "Wǒ xiǎng qù Běijīng lǚyóu.", "vi": "Tôi muốn đi Bắc Kinh du lịch."}]},
    {"simplified": "会", "traditional": "會", "pinyin": "huì", "hanviet": "hội", "meaning": "Biết (qua học tập), sẽ", "hsk": 1, "radical": "人 (Nhân)", "strokes": 6, "pos": "Trợ động từ", "examples": [{"zh": "我会说汉语。", "pinyin": "Wǒ huì shuō Hànyǔ.", "vi": "Tôi biết nói tiếng Hán."}]},
    {"simplified": "能", "traditional": "能", "pinyin": "néng", "hanviet": "năng", "meaning": "Có thể (năng lực, điều kiện)", "hsk": 1, "radical": "月 (Nguyệt)", "strokes": 10, "pos": "Trợ động từ", "examples": [{"zh": "我能借你的书吗？", "pinyin": "Wǒ néng jiè nǐ de shū ma?", "vi": "Tôi có thể mượn sách bạn không?"}]},

    # Nhóm 5: Thời gian & Nơi chốn
    {"simplified": "今天", "traditional": "今天", "pinyin": "jīntiān", "hanviet": "kim thiên", "meaning": "Hôm nay", "hsk": 1, "radical": "人 (Nhân)", "strokes": 8, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "今天天气很好。", "pinyin": "Jīntiān tiānqì hěn hǎo.", "vi": "Hôm nay thời tiết rất đẹp."}]},
    {"simplified": "明天", "traditional": "明天", "pinyin": "míngtiān", "hanviet": "minh thiên", "meaning": "Ngày mai", "hsk": 1, "radical": "日 (Nhật)", "strokes": 12, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "明天见！", "pinyin": "Míngtiān jiàn!", "vi": "Ngày mai gặp lại!"}]},
    {"simplified": "昨天", "traditional": "昨天", "pinyin": "zuótiān", "hanviet": "tạc thiên", "meaning": "Hôm qua", "hsk": 1, "radical": "日 (Nhật)", "strokes": 13, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "昨天我很忙。", "pinyin": "Zuótiān wǒ hěn máng.", "vi": "Hôm qua tôi rất bận."}]},
    {"simplified": "现在", "traditional": "現在", "pinyin": "xiànzài", "hanviet": "hiện tại", "meaning": "Bây giờ, hiện tại", "hsk": 1, "radical": "王 (Ngọc)", "strokes": 14, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "现在几点了？", "pinyin": "Xiànzài jǐ diǎn le?", "vi": "Bây giờ mấy giờ rồi?"}]},
    {"simplified": "早上", "traditional": "早上", "pinyin": "zǎoshang", "hanviet": "tảo thượng", "meaning": "Buổi sáng sớm", "hsk": 2, "radical": "日 (Nhật)", "strokes": 9, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "早上好！", "pinyin": "Zǎoshang hǎo!", "vi": "Chào buổi sáng!"}]},
    {"simplified": "晚上", "traditional": "晚上", "pinyin": "wǎnshang", "hanviet": "vãn thượng", "meaning": "Buổi tối", "hsk": 2, "radical": "日 (Nhật)", "strokes": 14, "pos": "Danh từ chỉ thời gian", "examples": [{"zh": "晚上我们一起吃饭吧。", "pinyin": "Wǎnshang wǒmen yìqǐ chī fàn ba.", "vi": "Tối nay chúng mình cùng ăn cơm nhé."}]},
    {"simplified": "年", "traditional": "年", "pinyin": "nián", "hanviet": "niên", "meaning": "Năm", "hsk": 1, "radical": "干 (Can)", "strokes": 6, "pos": "Danh từ / Lượng từ", "examples": [{"zh": "我在中国住了一年。", "pinyin": "Wǒ zài Zhōngguó zhù le yì nián.", "vi": "Tôi sống ở Trung Quốc một năm."}]},
    {"simplified": "月", "traditional": "月", "pinyin": "yuè", "hanviet": "nguyệt", "meaning": "Tháng, mặt trăng", "hsk": 1, "radical": "月 (Nguyệt)", "strokes": 4, "pos": "Danh từ", "examples": [{"zh": "下个月我回国。", "pinyin": "Xià gè yuè wǒ huí guó.", "vi": "Tháng sau tôi về nước."}]},
    {"simplified": "星期", "traditional": "星期", "pinyin": "xīngqī", "hanviet": "tinh kỳ", "meaning": "Tuần, thứ", "hsk": 1, "radical": "日 (Nhật)", "strokes": 21, "pos": "Danh từ", "examples": [{"zh": "这个星期很忙。", "pinyin": "Zhège xīngqī hěn máng.", "vi": "Tuần này rất bận."}]},
    {"simplified": "学校", "traditional": "學校", "pinyin": "xuéxiào", "hanviet": "học hiệu", "meaning": "Trường học", "hsk": 1, "radical": "木 (Mộc)", "strokes": 18, "pos": "Danh từ", "examples": [{"zh": "我们的学校很大。", "pinyin": "Wǒmen de xuéxiào hěn dà.", "vi": "Trường chúng tôi rất to."}]},
    {"simplified": "医院", "traditional": "醫院", "pinyin": "yīyuàn", "hanviet": "y viện", "meaning": "Bệnh viện", "hsk": 1, "radical": "阝 (Ấp)", "strokes": 16, "pos": "Danh từ", "examples": [{"zh": "去医院看病。", "pinyin": "Qù yīyuàn kànbìng.", "vi": "Đến bệnh viện khám bệnh."}]},
    {"simplified": "饭店", "traditional": "飯店", "pinyin": "fàndiàn", "hanviet": "phạn điếm", "meaning": "Nhà hàng, quán ăn, khách sạn", "hsk": 1, "radical": "广 (Quảng)", "strokes": 15, "pos": "Danh từ", "examples": [{"zh": "我们在饭店门口见。", "pinyin": "Wǒmen zài fàndiàn ménkǒu jiàn.", "vi": "Chúng ta gặp nhau trước cửa nhà hàng."}]},
    {"simplified": "商店", "traditional": "商店", "pinyin": "shāngdiàn", "hanviet": "thương điếm", "meaning": "Cửa hàng, tiệm tạp hóa", "hsk": 1, "radical": "广 (Quảng)", "strokes": 19, "pos": "Danh từ", "examples": [{"zh": "去商店买水果。", "pinyin": "Qù shāngdiàn mǎi shuǐguǒ.", "vi": "Đến cửa hàng mua hoa quả."}]},

    # Nhóm 6: Tính từ & Trạng từ quan trọng
    {"simplified": "大", "traditional": "大", "pinyin": "dà", "hanviet": "đại", "meaning": "To, lớn", "hsk": 1, "radical": "大 (Đại)", "strokes": 3, "pos": "Tính từ", "examples": [{"zh": "这个苹果很大。", "pinyin": "Zhège píngguǒ hěn dà.", "vi": "Quả táo này rất to."}]},
    {"simplified": "小", "traditional": "小", "pinyin": "xiǎo", "hanviet": "tiểu", "meaning": "Nhỏ, bé", "hsk": 1, "radical": "小 (Tiểu)", "strokes": 3, "pos": "Tính từ", "examples": [{"zh": "猫很小。", "pinyin": "Māo hěn xiǎo.", "vi": "Con mèo rất nhỏ."}]},
    {"simplified": "多", "traditional": "多", "pinyin": "duō", "hanviet": "đa", "meaning": "Nhiều", "hsk": 1, "radical": "夕 (Tịch)", "strokes": 6, "pos": "Tính từ", "examples": [{"zh": "这里的人很多。", "pinyin": "Zhèlǐ de rén hěn duō.", "vi": "Người ở đây rất nhiều."}]},
    {"simplified": "少", "traditional": "少", "pinyin": "shǎo", "hanviet": "thiểu", "meaning": "Ít", "hsk": 1, "radical": "小 (Tiểu)", "strokes": 4, "pos": "Tính từ", "examples": [{"zh": "时间很少。", "pinyin": "Shíjiān hěn shǎo.", "vi": "Thời gian còn rất ít."}]},
    {"simplified": "热", "traditional": "熱", "pinyin": "rè", "hanviet": "nhiệt", "meaning": "Nóng, nhiệt độ cao", "hsk": 1, "radical": "灬 (Hỏa)", "strokes": 10, "pos": "Tính từ", "examples": [{"zh": "今天太热了！", "pinyin": "Jīntiān tài rè le!", "vi": "Hôm nay nóng quá!"}]},
    {"simplified": "冷", "traditional": "冷", "pinyin": "lěng", "hanviet": "lãnh", "meaning": "Lạnh, buốt", "hsk": 1, "radical": "冫 (Băng)", "strokes": 7, "pos": "Tính từ", "examples": [{"zh": "冬天很冷。", "pinyin": "Dōngtiān hěn lěng.", "vi": "Mùa đông rất lạnh."}]},
    {"simplified": "漂亮", "traditional": "漂亮", "pinyin": "piàoliang", "hanviet": "phiêu lượng", "meaning": "Xinh đẹp, đẹp đẽ", "hsk": 1, "radical": "氵 (Thủy)", "strokes": 23, "pos": "Tính từ", "examples": [{"zh": "这件衣服真漂亮！", "pinyin": "Zhè jiàn yīfu zhēn piàoliang!", "vi": "Bộ đồ này đẹp thật đấy!"}]},
    {"simplified": "高兴", "traditional": "高興", "pinyin": "gāoxìng", "hanviet": "cao hứng", "meaning": "Vui vẻ, hân hoan", "hsk": 1, "radical": "高 (Cao)", "strokes": 16, "pos": "Tính từ", "examples": [{"zh": "认识你我很高兴。", "pinyin": "Rènshi nǐ wǒ hěn gāoxìng.", "vi": "Rất vui được quen bạn."}]},
    {"simplified": "快", "traditional": "快", "pinyin": "kuài", "hanviet": "khoái", "meaning": "Nhanh, mau", "hsk": 2, "radical": "忄 (Tâm)", "strokes": 7, "pos": "Tính từ", "examples": [{"zh": "他跑得很快。", "pinyin": "Tā pǎo de hěn kuài.", "vi": "Anh ấy chạy rất nhanh."}]},
    {"simplified": "慢", "traditional": "慢", "pinyin": "màn", "hanviet": "mạn", "meaning": "Chậm chạp, từ từ", "hsk": 2, "radical": "忄 (Tâm)", "strokes": 14, "pos": "Tính từ", "examples": [{"zh": "请说慢一点儿。", "pinyin": "Qǐng shuō màn yìdiǎnr.", "vi": "Xin nói chậm một chút."}]},
    {"simplified": "累", "traditional": "累", "pinyin": "lèi", "hanviet": "luy", "meaning": "Mệt mỏi", "hsk": 2, "radical": "田 (Điền)", "strokes": 11, "pos": "Tính từ", "examples": [{"zh": "工作了一天，很累。", "pinyin": "Gōngzuò le yì tiān, hěn lèi.", "vi": "Làm việc cả ngày, mệt lắm."}]}
]

# NGÂN HÀNG BÀI TẬP ĐA DẠNG (NHIỀU DẠNG BÀI, NHIỀU ĐỘ KHÓ)
# Dạng bài:
# 1. 'reorder': Sắp xếp trật tự từ ghép thành câu hoàn chỉnh
# 2. 'cloze': Điền từ vào chỗ trống trong câu
# 3. 'true_false': Nhận định Đúng/Sai
# 4. 'listening': Luyện nghe hiểu
# 5. 'meaning': Nghĩa từ vựng ngữ cảnh
# 6. 'pinyin': Phiên âm chuẩn
EXPANDED_QUIZZES = [
    # --- MỨC ĐỘ DỄ (Cơ bản / HSK 1) ---
    {
        "level": 1,
        "difficulty": "easy",
        "type": "reorder",
        "question": "Sắp xếp các từ sau thành câu hoàn chỉnh:",
        "target_word": "我是学生",
        "pinyin_hint": "wǒ shì xuésheng",
        "options": ["我", "是", "学生"],
        "correct_index": 0,
        "explanation": "Cấu trúc câu khẳng định cơ bản: [Chủ ngữ] + 是 + [Tân ngữ] -> 我是学生 (Tôi là học sinh).",
        "extra_data": {
            "tokens": ["学生", "我", "是"],
            "correct_order": ["我", "是", "学生"],
            "full_sentence": "我是学生。"
        }
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "cloze",
        "question": "Chọn từ thích hợp điền vào chỗ trống: \"你好！认识你很 ( )。\"",
        "target_word": "高兴",
        "pinyin_hint": "gāoxìng",
        "options": ["高兴 (vui vẻ)", "累 (mệt)", "贵 (đắt)", "忙 (bận)"],
        "correct_index": 0,
        "explanation": "Thành ngữ chào hỏi xã giao quen thuộc: 认识你很高兴 (Rất vui được làm quen với bạn)."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Cụm từ \"明天见\" có nghĩa là \"Hẹn gặp lại vào ngày mai\".",
        "target_word": "明天见",
        "pinyin_hint": "míngtiān jiàn",
        "options": ["Đúng", "Sai"],
        "correct_index": 0,
        "explanation": "Đúng! 明天 (ngày mai) + 见 (gặp) = Ngày mai gặp lại."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "listening",
        "question": "Nghe phát âm và chọn ý nghĩa tiếng Việt chính xác của câu sau:",
        "target_word": "你吃米饭吗？",
        "pinyin_hint": "nǐ chī mǐfàn ma?",
        "options": ["Bạn có ăn cơm trắng không?", "Bạn muốn uống nước không?", "Bạn đi đâu đấy?", "Cơm này bao nhiêu tiền?"],
        "correct_index": 0,
        "explanation": "你 (bạn) + 吃 (ăn) + 米饭 (cơm) + 吗 (không?)."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "reorder",
        "question": "Sắp xếp các từ sau thành câu chào hỏi chuẩn:",
        "target_word": "老师您好",
        "pinyin_hint": "lǎoshī nín hǎo",
        "options": ["老师", "您", "好"],
        "correct_index": 0,
        "explanation": "Chào giáo viên lịch sự: 老师，您好！(Em chào thầy/cô ạ).",
        "extra_data": {
            "tokens": ["好", "您", "老师"],
            "correct_order": ["老师", "您", "好"],
            "full_sentence": "老师您好！"
        }
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "cloze",
        "question": "Điền từ thích hợp vào chỗ trống: \"天气太热了，我想 ( ) 一杯水。\"",
        "target_word": "喝",
        "pinyin_hint": "hē",
        "options": ["喝 (uống)", "吃 (ăn)", "看 (xem)", "买 (mua)"],
        "correct_index": 0,
        "explanation": "Nước (水) đi với hành động uống (喝): 喝一杯水 (uống một cốc nước)."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Từ \"谢谢\" đọc pinyin là \"xièxie\" mang nghĩa là \"Xin lỗi\".",
        "target_word": "谢谢",
        "pinyin_hint": "xièxie",
        "options": ["Đúng", "Sai"],
        "correct_index": 1,
        "explanation": "Sai! 谢谢 có nghĩa là 'Cảm ơn', còn 'Xin lỗi' trong tiếng Trung là 对不起 (duìbuqǐ)."
    },

    # --- MỨC ĐỘ TRUNG BÌNH (HSK 2) ---
    {
        "level": 2,
        "difficulty": "medium",
        "type": "reorder",
        "question": "Sắp xếp các từ sau thành câu hỏi thời gian đúng:",
        "target_word": "现在几点了",
        "pinyin_hint": "xiànzài jǐ diǎn le",
        "options": ["现在", "几点", "了"],
        "correct_index": 0,
        "explanation": "Câu hỏi giờ tiêu chuẩn: 现在几点了？ (Bây giờ mấy giờ rồi?).",
        "extra_data": {
            "tokens": ["了", "几点", "现在"],
            "correct_order": ["现在", "几点", "了"],
            "full_sentence": "现在几点了？"
        }
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "cloze",
        "question": "Chọn từ điền vào chỗ trống: \"这个苹果六块钱一斤，太 ( ) 了，便宜点儿吧！\"",
        "target_word": "贵",
        "pinyin_hint": "guì",
        "options": ["贵 (đắt)", "便宜 (rẻ)", "大 (to)", "甜 (ngọt)"],
        "correct_index": 0,
        "explanation": "Vì vế sau là '便宜点儿吧' (Rẻ hơn chút đi) nên vế trước phải là chê đắt: 太贵了 (Đắt quá)."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "reorder",
        "question": "Sắp xếp câu liên động: \"Đi thư viện đọc sách\"",
        "target_word": "我去图书馆看书",
        "pinyin_hint": "wǒ qù túshūguǎn kàn shū",
        "options": ["我", "去", "图书馆", "看书"],
        "correct_index": 0,
        "explanation": "Cấu trúc liên động: [Chủ ngữ] + 去 + [Nơi chốn] + [Hành động] -> 我去图书馆看书。",
        "extra_data": {
            "tokens": ["看书", "去", "我", "图书馆"],
            "correct_order": ["我", "去", "图书馆", "看书"],
            "full_sentence": "我去图书馆看书。"
        }
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "listening",
        "question": "Nghe câu sau và cho biết nhân vật đang muốn đi đâu:",
        "target_word": "下午我去银行取钱。",
        "pinyin_hint": "xiàwǔ wǒ qù yínháng qǔ qián",
        "options": ["Đến ngân hàng rút tiền", "Đến trường học tập", "Đến bệnh viện khám bệnh", "Về ký túc xá nghỉ ngơi"],
        "correct_index": 0,
        "explanation": "银行 (yínháng - ngân hàng) + 取钱 (qǔ qián - rút tiền)."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Trong tiếng Trung, 1 斤 (cân) bằng 1.000 gram (1 kg).",
        "target_word": "斤",
        "pinyin_hint": "jīn",
        "options": ["Đúng", "Sai"],
        "correct_index": 1,
        "explanation": "Sai! Đơn vị 1 斤 (cân) của Trung Quốc chỉ bằng 500 gram (nửa kg). 1 kg chuẩn là 一公斤."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "cloze",
        "question": "Chọn lượng từ thích hợp: \"服务员，请给我两 ( ) 米饭和一 ( ) 绿茶。\"",
        "target_word": "碗 / 杯",
        "pinyin_hint": "wǎn / bēi",
        "options": ["碗 / 杯 (bát / ly)", "个 / 瓶", "斤 / 块", "本 / 张"],
        "correct_index": 0,
        "explanation": "Lượng từ của cơm là 碗 (bát), lượng từ của trà là 杯 (ly/tách)."
    },

    # --- MỨC ĐỘ KHÓ / NÂNG CAO (HSK 3 - 4) ---
    {
        "level": 3,
        "difficulty": "hard",
        "type": "reorder",
        "question": "Sắp xếp câu phức có phó từ chỉ thời gian và địa điểm:",
        "target_word": "昨天我们都在家看书",
        "pinyin_hint": "zuótiān wǒmen dōu zài jiā kàn shū",
        "options": ["昨天", "我们", "都", "在", "家", "看书"],
        "correct_index": 0,
        "explanation": "Trật tự câu tiếng Trung: [Thời gian] + [Chủ ngữ] + [Phó từ 都] + [Tại địa điểm 在家] + [Hành động 看书].",
        "extra_data": {
            "tokens": ["在家", "看书", "我们", "昨天", "都"],
            "correct_order": ["昨天", "我们", "都", "在家", "看书"],
            "full_sentence": "昨天我们都在家看书。"
        }
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "reorder",
        "question": "Sắp xếp câu so sánh hơn với chữ 比 (bǐ):",
        "target_word": "我哥哥比我大两岁",
        "pinyin_hint": "wǒ gēge bǐ wǒ dà liǎng suì",
        "options": ["我哥哥", "比", "我", "大", "两岁"],
        "correct_index": 0,
        "explanation": "Cấu trúc so sánh: A + 比 + B + [Tính từ] + [Số lượng chênh lệch] -> 我哥哥比我大两岁 (Anh trai lớn hơn tôi 2 tuổi).",
        "extra_data": {
            "tokens": ["两岁", "我", "比", "大", "我哥哥"],
            "correct_order": ["我哥哥", "比", "我", "大", "两岁"],
            "full_sentence": "我哥哥比我大两岁。"
        }
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "cloze",
        "question": "Chọn liên từ thích hợp: \"( ) 昨天下了大雨，( ) 我们没有去公园。\"",
        "target_word": "因为 / 所以",
        "pinyin_hint": "yīnwèi / suǒyǐ",
        "options": ["因为 / 所以 (Bởi vì... cho nên...)", "虽然 / 但是 (Mặc dù... nhưng...)", "不但 / 而且 (Không những... mà còn...)", "如果 / 就 (Nếu... thì...)"],
        "correct_index": 0,
        "explanation": "Cặp liên từ biểu thị quan hệ nguyên nhân - kết quả: 因为 (Bởi vì) ... 所以 (Cho nên)."
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "listening",
        "question": "Nghe đoạn hội thoại ngắn và chọn câu nhận định chính xác nhất:",
        "target_word": "虽然这个问题很难，但是只要我们坚持，就一定会成功解决。",
        "pinyin_hint": "suīrán zhège wèntí hěn nán, dànshì zhǐyào wǒmen jiānchí, jiù yídìng huì chénggōng jiějué.",
        "options": [
            "Chỉ cần kiên trì thì vấn đề khó khăn này nhất định sẽ giải quyết thành công",
            "Vấn đề này quá khó nên chúng tôi quyết định bỏ cuộc",
            "Mọi việc đã xong từ hôm qua rồi",
            "Không ai có thể giải quyết được vấn đề này"
        ],
        "correct_index": 0,
        "explanation": "Cặp từ '虽然...但是...' (tuy rằng... nhưng...) kết hợp '只要...就...' (chỉ cần... thì...)."
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Trong câu hỏi chính phản tiếng Trung, có thể dùng trợ từ \"吗\" ở cuối câu, ví dụ: \"你忙不忙吗？\"",
        "target_word": "忙不忙",
        "pinyin_hint": "máng bu máng",
        "options": ["Đúng", "Sai"],
        "correct_index": 1,
        "explanation": "Sai! Câu hỏi chính phản (A không A) đã tự mang tính nghi vấn rồi, TUYỆT ĐỐI KHÔNG được thêm chữ '吗' ở cuối câu nữa. Câu đúng là: 你忙不忙？"
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "cloze",
        "question": "Điền từ thích hợp vào câu chữ 把 (câu xử lý): \"请你把这本书 ( ) 他。\"",
        "target_word": "给",
        "pinyin_hint": "gěi",
        "options": ["给 (đưa cho)", "看 (xem)", "买 (mua)", "想 (nghĩ)"],
        "correct_index": 0,
        "explanation": "Cấu trúc câu chữ 把 biểu thị sự tác động / chuyển giao: 把 + [Vật] + 给 + [Người] -> 把这本书给他 (Đưa cuốn sách này cho anh ấy)."
    },
    # --- CÂU HỎI BỔ SUNG ĐA DẠNG HƠN ---
    {
        "level": 1,
        "difficulty": "easy",
        "type": "reorder",
        "question": "Sắp xếp thành câu biểu đạt mong muốn ăn uống:",
        "target_word": "我想吃面条",
        "pinyin_hint": "wǒ xiǎng chī miàntiáo",
        "options": ["我想", "吃", "面条"],
        "correct_index": 0,
        "explanation": "Cấu trúc: [Chủ ngữ] + 想 + [Động từ] + [Tân ngữ] -> 我想吃面条 (Tôi muốn ăn mì).",
        "extra_data": {
            "tokens": ["面条", "吃", "我想"],
            "correct_order": ["我想", "吃", "面条"],
            "full_sentence": "我想吃面条。"
        }
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "cloze",
        "question": "Điền số thứ tự vào chỗ trống: \"今天星期 ( )，明天是星期天。\"",
        "target_word": "六",
        "pinyin_hint": "liù",
        "options": ["六 (Thứ Bảy)", "五 (Thứ Sáu)", "一 (Thứ Hai)", "四 (Thứ Năm)"],
        "correct_index": 0,
        "explanation": "Trước Chủ nhật (星期天) là Thứ Bảy (星期六)."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "listening",
        "question": "Nghe câu sau và chọn lời dịch phù hợp nhất:",
        "target_word": "请进，请坐，请喝茶！",
        "pinyin_hint": "qǐng jìn, qǐng zuò, qǐng hē chá!",
        "options": [
            "Mời vào, mời ngồi, mời uống trà!",
            "Cảm ơn bạn, tôi không uống trà đâu.",
            "Tạm biệt, ngày mai gặp lại nhé!",
            "Bạn tên là gì vậy?"
        ],
        "correct_index": 0,
        "explanation": "请进 (mời vào), 请坐 (mời ngồi), 请喝茶 (mời uống trà) là 3 câu mời khách kinh điển của người Trung Quốc."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Từ \"医生\" (yīshēng) có nghĩa là giáo viên.",
        "target_word": "医生",
        "pinyin_hint": "yīshēng",
        "options": ["Đúng", "Sai"],
        "correct_index": 1,
        "explanation": "Sai! 医生 là Bác sĩ. Giáo viên trong tiếng Trung là 老师 (lǎoshī)."
    },
    {
        "level": 1,
        "difficulty": "easy",
        "type": "meaning",
        "question": "Cụm từ \"多少钱\" (duōshao qián) thường dùng trong tình huống nào?",
        "target_word": "多少钱",
        "pinyin_hint": "duōshao qián",
        "options": ["Hỏi giá tiền khi mua sắm", "Hỏi thăm sức khỏe", "Hỏi đường đi", "Hỏi thời gian"],
        "correct_index": 0,
        "explanation": "多少钱 (bao nhiêu tiền) là cụm từ chuyên dùng để hỏi giá khi mua bán."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "reorder",
        "question": "Sắp xếp câu đi chợ mua hoa quả:",
        "target_word": "我想买两斤苹果",
        "pinyin_hint": "wǒ xiǎng mǎi liǎng jīn píngguǒ",
        "options": ["我", "想买", "两斤", "苹果"],
        "correct_index": 0,
        "explanation": "Cấu trúc: [Chủ ngữ] + [Động từ] + [Số lượng từ] + [Danh từ] -> 我想买两斤苹果 (Tôi muốn mua 2 cân táo).",
        "extra_data": {
            "tokens": ["两斤", "苹果", "我想买"],
            "correct_order": ["我想买", "两斤", "苹果"],
            "full_sentence": "我想买两斤苹果。"
        }
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "cloze",
        "question": "Chọn từ điền vào chỗ trống: \"昨天工作太累了，所以我今天不想 ( )。\"",
        "target_word": "上班",
        "pinyin_hint": "shàngbān",
        "options": ["上班 (đi làm)", "睡觉 (ngủ)", "休息 (nghỉ ngơi)", "喝茶 (uống trà)"],
        "correct_index": 0,
        "explanation": "Hôm qua quá mệt nên hôm nay không muốn đi làm (上班)."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "listening",
        "question": "Nghe câu hỏi lựa chọn và chọn câu trả lời đúng ngữ cảnh:",
        "target_word": "你想喝咖啡还是中国茶？",
        "pinyin_hint": "nǐ xiǎng hē kāfēi háishi Zhōngguó chá?",
        "options": [
            "Bạn muốn uống cà phê hay là trà Trung Quốc?",
            "Cà phê này bao nhiêu tiền một ly?",
            "Trà Trung Quốc rất thơm ngon.",
            "Tôi không thích uống cà phê."
        ],
        "correct_index": 0,
        "explanation": "Cấu trúc câu hỏi lựa chọn với 还是 (hay là): A 还是 B."
    },
    {
        "level": 2,
        "difficulty": "medium",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Trong tiếng Trung, khi nói mốc thời gian, người ta nói \"Tháng\" trước rồi mới đến \"Ngày\".",
        "target_word": "月/日",
        "pinyin_hint": "yuè / rì",
        "options": ["Đúng", "Sai"],
        "correct_index": 0,
        "explanation": "Đúng! Tiếng Trung sắp xếp từ lớn đến nhỏ: Năm -> Tháng -> Ngày."
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "reorder",
        "question": "Sắp xếp câu có trạng ngữ chỉ thời gian đứng đầu:",
        "target_word": "星期六我们想去看电影",
        "pinyin_hint": "xīngqīliù wǒmen xiǎng qù kàn diànyǐng",
        "options": ["星期六", "我们", "想去", "看电影"],
        "correct_index": 0,
        "explanation": "Trật tự câu: [Thời gian 星期六] + [Chủ ngữ 我们] + [Động từ năng nguyện 想去] + [Hành động 看电影].",
        "extra_data": {
            "tokens": ["看电影", "想去", "星期六", "我们"],
            "correct_order": ["星期六", "Chúng tôi", "想去", "看电影"],
            "correct_order": ["星期六", "我们", "想去", "看电影"],
            "full_sentence": "星期六我们想去看电影。"
        }
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "cloze",
        "question": "Chọn cặp liên từ biểu thị điều kiện: \"( ) 坚持努力学习，( ) 一定能学好汉语。\"",
        "target_word": "只要 / 就",
        "pinyin_hint": "zhǐyào / jiù",
        "options": ["只要 / 就 (Chỉ cần... thì...)", "因为 / 所以 (Vì... nên...)", "虽然 / 但是 (Tuy... nhưng...)", "即使 / 也 (Cho dù... cũng...)"],
        "correct_index": 0,
        "explanation": "只要...就... là cặp liên từ biểu thị điều kiện đủ: Chỉ cần kiên trì thì nhất định sẽ học tốt."
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "true_false",
        "question": "Nhận định sau Đúng hay Sai: Câu \"我想家\" có nghĩa là \"Tôi muốn đi đến nhà\".",
        "target_word": "想家",
        "pinyin_hint": "xiǎng jiā",
        "options": ["Đúng", "Sai"],
        "correct_index": 1,
        "explanation": "Sai! '想家' (xiǎng jiā) là một cụm từ cố định mang nghĩa 'Nhớ nhà, nhớ gia đình', chứ không phải muốn đi đến nhà."
    },
    {
        "level": 3,
        "difficulty": "hard",
        "type": "listening",
        "question": "Nghe đoạn văn ngắn và chọn câu tóm tắt chính xác:",
        "target_word": "虽然现在工作很忙，但他每天晚上都坚持学习一个小时汉语。",
        "pinyin_hint": "suīrán xiànzài gōngzuò hěn máng, dànshì tā měitiān wǎnshang dōu jiānchí xuéxí yí gè xiǎoshí Hànyǔ.",
        "options": [
            "Dù công việc rất bận nhưng mỗi tối anh ấy đều kiên trì học tiếng Hán 1 tiếng",
            "Công việc quá bận nên anh ấy đã dừng việc học tiếng Hán",
            "Mỗi tối anh ấy đều phải làm thêm một tiếng ở công ty",
            "Anh ấy không thích học tiếng Hán nữa"
        ],
        "correct_index": 0,
        "explanation": "坚持 (kiên trì) + 学习一个小时 (học một tiếng đồng hồ)."
    }
]

def seed_full_system():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. CẬP NHẬT SCHEMA BẢNG QUIZZES ĐỂ HỖ TRỢ ĐA DẠNG DẠNG BÀI & ĐỘ KHÓ
    cursor.execute("PRAGMA table_info(quizzes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "difficulty" not in columns:
        cursor.execute("ALTER TABLE quizzes ADD COLUMN difficulty TEXT DEFAULT 'easy'")
    if "extra_data" not in columns:
        cursor.execute("ALTER TABLE quizzes ADD COLUMN extra_data TEXT DEFAULT '{}'")

    # 2. NẠP HƠN 70 TỪ VỰNG PHONG PHÚ VÀO BẢNG WORDS
    print("Đang nạp hơn 70 từ vựng phong phú vào cơ sở dữ liệu...")
    for w in EXPANDED_WORDS:
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
            w["hsk"],
            w.get("radical", ""),
            w.get("strokes", 0),
            w.get("pos", ""),
            json.dumps(w.get("examples", []), ensure_ascii=False)
        ))

    # 3. NẠP NGÂN HÀNG CÂU HỎI BÀI TẬP PHONG PHÚ ĐA DẠNG DẠNG BÀI
    print("Đang nạp ngân hàng bài tập lớn theo các mức độ khó và nhiều dạng đề...")
    cursor.execute("DELETE FROM quizzes") # Reset ngân hàng bài tập
    for q in EXPANDED_QUIZZES:
        cursor.execute("""
        INSERT INTO quizzes (level, difficulty, type, question, target_word, pinyin_hint, options, correct_index, explanation, extra_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["level"],
            q.get("difficulty", "easy"),
            q["type"],
            q["question"],
            q.get("target_word", ""),
            q.get("pinyin_hint", ""),
            json.dumps(q["options"], ensure_ascii=False),
            q["correct_index"],
            q.get("explanation", ""),
            json.dumps(q.get("extra_data", {}), ensure_ascii=False)
        ))

    conn.commit()
    conn.close()
    print("Đã nạp thành công toàn bộ từ vựng và hệ thống bài tập đa dạng!")

if __name__ == "__main__":
    seed_full_system()
