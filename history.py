import streamlit as st
from openai import OpenAI
import json

# ==========================================
# 1. 配置区域
# ==========================================
# 🔴 请填入你的 Key
API_KEY = "sk-56629665e59447f6a67f8a33e6bcdbde" 
BASE_URL = "https://api.deepseek.com"

# ==========================================
# 2. 全朝代历史数据库 (V4.1 严格分朝代版)
# ==========================================
# 结构：每个朝代都有 [皇帝, 大臣, 妃子, 文人, 典故, 语文课本] 6个分类
HISTORY_DATA = {
  "夏朝": {
    "👑 皇帝": ["大禹", "启", "桀"],
    "🧠 大臣": ["伯益", "关龙逄"],
    "💅 妃子": ["妺喜"],
    "✍️ 文人": ["(此时期记载较少)"],
    "📜 典故": ["大禹治水", "三过家门而不入", "禅让制", "时日曷丧"],
    "📚 语文课本": ["(暂无直接课文，多见于史书引用)"]
  },
  "商朝": {
    "👑 皇帝": ["成汤", "盘庚", "武丁", "帝辛(纣王)"],
    "🧠 大臣": ["伊尹", "比干", "箕子", "姜子牙(早期)"],
    "💅 妃子": ["妇好", "妲己"],
    "✍️ 文人": ["(甲骨文时期)"],
    "📜 典故": ["酒池肉林", "助纣为虐", "姜太公钓鱼", "愿者上钩"],
    "📚 语文课本": ["《封神演义》(相关文学)", "《诗经·商颂》(选)"]
  },
  "周朝": {
    "👑 皇帝": ["周武王", "周公旦", "周幽王", "周平王"],
    "🧠 大臣": ["姜尚", "管仲", "鲍叔牙", "伍子胥"],
    "💅 妃子": ["褒姒", "西施(春秋)"],
    "✍️ 文人": ["老子", "孔子", "孟子", "庄子", "屈原", "墨子", "韩非子"],
    "📜 典故": ["烽火戏诸侯", "卧薪尝胆", "退避三舍", "围魏救赵", "负荆请罪", "完璧归赵", "毛遂自荐", "纸上谈兵"],
    "📚 语文课本": ["《诗经·采薇》", "《论语》十则", "《生于忧患，死于安乐》", "《曹刿论战》", "《离骚》", "《逍遥游》", "《劝学》", "《廉颇蔺相如列传》", "《邹忌讽齐王纳谏》"]
  },
  "秦朝": {
    "👑 皇帝": ["秦始皇", "秦二世"],
    "🧠 大臣": ["李斯", "蒙恬", "王翦", "赵高", "吕不韦", "商鞅(前秦)"],
    "💅 妃子": ["(史料记载较少)"],
    "✍️ 文人": ["韩非"],
    "📜 典故": ["商鞅变法", "图穷匕见", "指鹿为马", "焚书坑儒", "孟姜女哭长城", "一字千金"],
    "📚 语文课本": ["《过秦论》", "《谏逐客书》", "《荆轲刺秦王》", "《阿房宫赋》(杜牧写秦)"]
  },
  "西汉": {
    "👑 皇帝": ["刘邦", "刘彻(汉武帝)", "刘询(汉宣帝)"],
    "🧠 大臣": ["萧何", "张良", "韩信", "霍去病", "卫青", "张骞", "苏武", "霍光"],
    "💅 妃子": ["吕雉", "卫子夫", "赵飞燕", "王政君"],
    "✍️ 文人": ["司马迁", "贾谊", "司马相如", "东方朔"],
    "📜 典故": ["明修栈道暗度陈仓", "四面楚歌", "成也萧何败也萧何", "金屋藏娇", "封狼居胥", "苏武牧羊", "断袖之癖"],
    "📚 语文课本": ["《鸿门宴》", "《报任安书》", "《苏武传》", "《李将军列传》", "《过秦论》(贾谊)"]
  },
  "东汉": {
    "👑 皇帝": ["刘秀", "刘协(汉献帝)"],
    "🧠 大臣": ["班超", "马援", "梁冀", "何进", "董卓"],
    "💅 妃子": ["阴丽华", "梁妠"],
    "✍️ 文人": ["张衡", "蔡伦", "班固", "孔融"],
    "📜 典故": ["投笔从戎", "马革裹尸", "不入虎穴焉得虎子", "举案齐眉", "让梨的故事"],
    "📚 语文课本": ["《张衡传》", "《孔雀东南飞》"]
  },
  "三国": {
    "👑 皇帝": ["曹操", "刘备", "孙权", "曹丕"],
    "🧠 大臣": ["诸葛亮", "关羽", "张飞", "赵云", "周瑜", "司马懿", "荀彧", "鲁肃"],
    "💅 妃子": ["甄宓", "孙尚香", "大乔", "小乔"],
    "✍️ 文人": ["曹植", "王粲", "祢衡", "陈寿"],
    "📜 典故": ["桃园三结义", "三顾茅庐", "火烧赤壁", "草船借箭", "白衣渡江", "乐不思蜀", "七步成诗", "望梅止渴", "刮目相看", "既生瑜何生亮"],
    "📚 语文课本": ["《出师表》", "《赤壁赋》(苏轼写三国)", "《短歌行》", "《观沧海》", "《隆中对》", "《陈情表》"]
  },
  "两晋南北朝": {
    "👑 皇帝": ["司马炎", "司马睿", "拓跋焘", "萧衍"],
    "🧠 大臣": ["谢安", "王导", "祖逖", "桓温", "兰陵王"],
    "💅 妃子": ["贾南风", "冯小怜"],
    "✍️ 文人": ["王羲之", "陶渊明", "谢灵运", "祖冲之", "郦道元", "刘义庆"],
    "📜 典故": ["闻鸡起舞", "草木皆兵", "东床快婿", "入木三分", "不为五斗米折腰", "画龙点睛"],
    "📚 语文课本": ["《归去来兮辞》", "《桃花源记》", "《兰亭集序》", "《木兰诗》", "《水经注》", "《世说新语》"]
  },
  "隋朝": {
    "👑 皇帝": ["杨坚", "杨广"],
    "🧠 大臣": ["杨素", "韩擒虎", "贺若弼"],
    "💅 妃子": ["萧皇后"],
    "✍️ 文人": ["薛道衡"],
    "📜 典故": ["罄竹难书", "开科取士"],
    "📚 语文课本": ["《赵州桥》(说明文)"]
  },
  "唐朝": {
    "👑 皇帝": ["李渊", "李世民", "武则天", "李隆基"],
    "🧠 大臣": ["魏征", "房玄龄", "杜如晦", "李靖", "郭子仪", "颜真卿"],
    "💅 妃子": ["长孙皇后", "杨贵妃", "上官婉儿"],
    "✍️ 文人": ["李白", "杜甫", "白居易", "王维", "韩愈", "柳宗元", "杜牧", "李商隐"],
    "📜 典故": ["玄武门之变", "贞观之治", "请君入瓮", "贵妃醉酒", "一骑红尘妃子笑", "安史之乱", "黄粱一梦", "口蜜腹剑"],
    "📚 语文课本": ["《师说》", "《长恨歌》", "《琵琶行》", "《蜀道难》", "《将进酒》", "《茅屋为秋风所破歌》", "《滕王阁序》", "《阿房宫赋》", "《陋室铭》", "《马说》"]
  },
  "宋朝": {
    "👑 皇帝": ["赵匡胤", "赵光义", "赵祯", "赵佶", "赵构"],
    "🧠 大臣": ["寇准", "范仲淹", "包拯", "王安石", "司马光", "岳飞", "文天祥"],
    "💅 妃子": ["刘娥", "李师师"],
    "✍️ 文人": ["苏轼", "欧阳修", "李清照", "朱熹", "辛弃疾", "陆游", "柳永"],
    "📜 典故": ["杯酒释兵权", "狸猫换太子", "精忠报国", "莫须有", "东窗事发", "程门立雪", "河东狮吼"],
    "📚 语文课本": ["《岳阳楼记》", "《醉翁亭记》", "《赤壁赋》", "《念奴娇·赤壁怀古》", "《水调歌头》", "《声声慢》", "《永遇乐·京口北固亭怀古》", "《石钟山记》"]
  },
  "元朝": {
    "👑 皇帝": ["忽必烈", "铁木真(成吉思汗)"],
    "🧠 大臣": ["耶律楚材", "伯颜", "脱脱"],
    "💅 妃子": ["赵敏(小说虚构)", "奇皇后"],
    "✍️ 文人": ["关汉卿", "马致远", "郭守敬", "王实甫"],
    "📜 典故": ["人生自古谁无死", "道路以目"],
    "📚 语文课本": ["《窦娥冤》", "《天净沙·秋思》"]
  },
  "明朝": {
    "👑 皇帝": ["朱元璋", "朱棣", "朱由检(崇祯)"],
    "🧠 大臣": ["郑和", "于谦", "海瑞", "张居正", "戚继光", "袁崇焕"],
    "💅 妃子": ["马皇后", "陈圆圆(明末)"],
    "✍️ 文人": ["宋濂", "王阳明", "归有光", "徐霞客", "李时珍", "吴承恩"],
    "📜 典故": ["火烧庆功楼", "靖难之役", "郑和下西洋", "土木堡之变", "粉身碎骨浑不怕", "东林党争"],
    "📚 语文课本": ["《项脊轩志》", "《送东阳马生序》", "《石灰吟》", "《核舟记》"]
  },
  "清朝": {
    "👑 皇帝": ["康熙", "雍正", "乾隆", "慈禧", "溥仪"],
    "🧠 大臣": ["和珅", "纪晓岚", "林则徐", "曾国藩", "左宗棠", "李鸿章"],
    "💅 妃子": ["孝庄文皇后", "珍妃"],
    "✍️ 文人": ["曹雪芹", "蒲松龄", "纳兰性德", "龚自珍", "梁启超", "鲁迅(清末)"],
    "📜 典故": ["文字狱", "康乾盛世", "虎门销烟", "垂帘听政", "戊戌六君子", "辛丑条约"],
    "📚 语文课本": ["《红楼梦》(选段)", "《登泰山记》", "《病梅馆记》", "《少年中国说》", "《狼》"]
  }
}

# ==========================================
# 3. 智能通用指令 (V4.1 - 严格引用版)
# ==========================================
PROMPT_V4 = """
你是一位博学、严谨、通俗的历史讲师（类似《百家讲坛》风格）。
用户会给你一个【朝代】和一个【关键词】（可能是人物、典故、或者课文标题）。
请先判断关键词的类型，然后严格按对应逻辑讲解：

### 情况 A：如果关键词是【历史人物】（皇帝、大臣、文人等）
1. **人物档案**：
   - 姓名、生卒大概年代。
   - **庙号**（如唐太宗）、**谥号**、**最高官职/封号**。
2. **核心定性**：
   - 用一句精辟的比喻或总结，概括他的一生。
3. **高光时刻（必须引用史料）**：
   - 选取该人物历史上最关键的 3-5 个转折点或大事件。
   - **格式要求**：对于每个事件，**必须先引用一句相关史料原文**（如《旧唐书》、《史记》、《资治通鉴》等），然后紧接着用**大白话**进行深度、通俗的解读。
   - 例如：
     > **玄武门之变**
     > *史料：“六月四日，公帅长孙无忌等入，伏兵于玄武门。”*
     > 解读：这一天，李世民带着兄弟们……

### 情况 B：如果关键词是【典故/成语/事件】（如“白衣渡江”）
1. **典故档案**：出处（哪本书）、涉及的主角。
2. **故事还原**：用生动的语言还原当时的场景。
3. **含义与用法**：解释这个典故现在的意思，或者它说明了什么道理。

### 情况 C：如果关键词是【语文课文/文学作品】（如《出师表》）
1. **作品名片**：作者、体裁、创作背景（当时发生了什么）。
2. **名句赏析**：摘录文中1-2句最经典的千古名句，并解释其含义。
3. **串联知识**：**这一点最重要！** 请解释这篇课文在历史上的地位，或者它反映了当时怎样的历史现象？帮助用户把“语文知识”和“历史知识”串联起来。

**通用禁令**：
- **严禁使用网络流行语**（如YYDS、绝绝子、显眼包等）。
- **严禁描写你的动作**（如“敲黑板”、“喝口水”、“推眼镜”等）。
- 引用史料要准确，解读要通俗但有深度。
"""

# ==========================================
# 4. 核心逻辑代码
# ==========================================

st.set_page_config(page_title="历史私教 V4.1", layout="wide", page_icon="📜")

if "history_messages" not in st.session_state: st.session_state.history_messages = []
if "current_item" not in st.session_state: st.session_state.current_item = None
if "story_content" not in st.session_state: st.session_state.story_content = ""
if "token_count" not in st.session_state: st.session_state.token_count = 0 

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- 侧边栏 ---
with st.sidebar:
    st.header("📜 全朝代传送门")
    era_list = list(HISTORY_DATA.keys())
    selected_era = st.selectbox("选择朝代", era_list)
    
    st.divider()
    cost_rmb = (st.session_state.token_count / 1000000) * 5
    st.metric("累计花费 (RMB)", f"¥{cost_rmb:.5f}", help="按DeepSeek API估算")

# --- 主界面 ---
st.title(f"📖 {selected_era} 百科全书")

# 切换朝代逻辑
if "last_era" not in st.session_state or st.session_state.last_era != selected_era:
    st.session_state.last_era = selected_era
    st.session_state.current_item = None
    st.session_state.story_content = ""
    st.session_state.history_messages = []

# 获取数据
era_data = HISTORY_DATA[selected_era]
categories = list(era_data.keys()) 

# 渲染选项卡 (Tabs)
tabs = st.tabs(categories)

for i, cat in enumerate(categories):
    with tabs[i]:
        # 显示分类说明
        if "典故" in cat: st.caption("💡 点击查看成语背后的真历史")
        if "课本" in cat: st.caption("📚 重温那些年背诵全文的噩梦与感动")
        
        cols = st.columns(4) # 这里的数字决定一行放几个按钮
        items = era_data[cat]
        for idx, item_name in enumerate(items):
            unique_key = f"{selected_era}_{cat}_{item_name}"
            if cols[idx % 4].button(item_name, key=unique_key):
                st.session_state.current_item = item_name
                st.session_state.story_content = ""
                st.session_state.history_messages = []
                st.rerun()

# --- 讲解区域 ---
if st.session_state.current_item:
    st.divider()
    st.header(f"🎙️ 深度解读：{st.session_state.current_item}")

    story_placeholder = st.empty()
    
    # 1. 生成讲解
    if not st.session_state.story_content:
        full_response = ""
        try:
            with st.spinner(f"AI 老师正在查阅史书：{st.session_state.current_item}..."):
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": PROMPT_V4},
                        {"role": "user", "content": f"朝代：{selected_era}，关键词：{st.session_state.current_item}"}
                    ],
                    stream=True
                )
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        story_placeholder.markdown(full_response + "▌")
                
                st.session_state.story_content = full_response
                st.session_state.token_count += int(len(full_response) * 1.5)
                story_placeholder.markdown(full_response)
                
                st.session_state.history_messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error(f"发生错误：{e}")
    else:
        story_placeholder.markdown(st.session_state.story_content)

    # 2. 自由对话
    st.divider()
    st.subheader("💬 举手提问")

    for msg in st.session_state.history_messages:
        if msg["content"] == st.session_state.story_content: continue 
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("没听懂？想知道更多？直接问！"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.history_messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            response_box = st.empty()
            full_reply = ""
            messages_to_send = [
                {"role": "system", "content": "你仍是那位博学的讲师。请结合上下文解答。"},
                {"role": "user", "content": f"背景：{st.session_state.story_content}"}
            ]
            for m in st.session_state.history_messages:
                 if m["content"] != st.session_state.story_content:
                     messages_to_send.append(m)

            stream = client.chat.completions.create(
                model="deepseek-chat", messages=messages_to_send, stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_reply += content
                    response_box.markdown(full_reply + "▌")
            
            response_box.markdown(full_reply)
            st.session_state.history_messages.append({"role": "assistant", "content": full_reply})
            st.session_state.token_count += int(len(full_reply) * 1.5)
            st.rerun()
