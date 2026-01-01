import streamlit as st
from openai import OpenAI
import json

# ==========================================
# 1. 配置区域
# ==========================================

# 🔴 请把你申请到的 DeepSeek API Key 填在引号里面
API_KEY = "sk-56629665e59447f6a67f8a33e6bcdbde" 
BASE_URL = "https://api.deepseek.com"

# ==========================================
# 2. 本地历史数据 (全朝代 V3.0版)
# ==========================================
HISTORY_DATA = {
  "夏朝": {
    "👑 皇帝": ["大禹", "启", "太康", "少康", "孔甲", "桀"],
    "🧠 大臣": ["伯益", "皋陶", "后稷", "关龙逄"],
    "💅 妃子": ["涂山氏", "妺喜"],
    "✍️ 文人": ["仪狄"]
  },
  "商朝": {
    "👑 皇帝": ["成汤", "太甲", "太戊", "盘庚", "武丁", "祖甲", "帝乙", "帝辛"],
    "🧠 大臣": ["伊尹", "仲虺", "傅说", "比干", "箕子", "微子"],
    "💅 妃子": ["妇好", "妲己"],
    "✍️ 文人": ["伊陟"]
  },
  "周朝": {
    "👑 皇帝": ["周武王", "周成王", "周穆王", "周厉王", "周幽王", "周平王", "周桓王", "周赧王"],
    "🧠 大臣": ["姜尚", "周公旦", "召公奭", "管仲", "伍子胥", "乐毅"],
    "💅 妃子": ["褒姒", "宣姜", "西施"],
    "✍️ 文人": ["老子", "孔子", "庄子", "孟子", "屈原", "墨子"]
  },
  "秦朝": {
    "👑 皇帝": ["秦始皇", "秦二世", "子婴"],
    "🧠 大臣": ["李斯", "蒙恬", "王翦", "章邯", "赵高", "冯去疾"],
    "💅 妃子": ["阿房女"],
    "✍️ 文人": ["吕不韦"]
  },
  "西汉": {
    "👑 皇帝": ["刘邦", "刘盈", "刘恒", "刘启", "刘彻", "刘弗陵", "刘询", "刘婴"],
    "🧠 大臣": ["萧何", "张良", "韩信", "周勃", "霍光", "张骞"],
    "💅 妃子": ["吕雉", "窦漪房", "卫子夫", "李夫人", "赵飞燕", "王政君"],
    "✍️ 文人": ["司马迁", "东方朔", "董仲舒", "扬雄", "司马相如"]
  },
  "东汉": {
    "👑 皇帝": ["刘秀", "刘庄", "刘炟", "刘肇", "刘志", "刘宏", "刘协"],
    "🧠 大臣": ["邓禹", "吴汉", "马援", "班超", "梁冀", "何进"],
    "💅 妃子": ["阴丽华", "郭圣通", "邓绥", "梁妠", "窦妙"],
    "✍️ 文人": ["班固", "张衡", "蔡邕", "蔡伦", "王充", "郑玄"]
  },
  "三国": {
    "👑 皇帝": ["曹丕", "曹叡", "刘备", "刘禅", "孙权", "孙皓"],
    "🧠 大臣": ["诸葛亮", "司马懿", "荀彧", "郭嘉", "周瑜", "陆逊", "关羽", "张飞"],
    "💅 妃子": ["甄宓", "甘夫人", "孙尚香", "大乔", "小乔"],
    "✍️ 文人": ["曹植", "王粲", "嵇康", "阮籍", "陈琳"]
  },
  "西晋": {
    "👑 皇帝": ["司马炎", "司马衷", "司马炽", "司马邺"],
    "🧠 大臣": ["羊祜", "杜预", "王浚", "贾充", "卫瓘", "张华"],
    "💅 妃子": ["杨艳", "贾南风", "羊献容"],
    "✍️ 文人": ["陆机", "潘岳", "左思", "郭璞"]
  },
  "东晋": {
    "👑 皇帝": ["司马睿", "司马绍", "司马衍", "司马昱", "司马曜", "司马德文"],
    "🧠 大臣": ["王导", "谢安", "桓温", "祖逖", "陶侃", "谢玄"],
    "💅 妃子": ["庾文君", "褚蒜子", "谢道韫"],
    "✍️ 文人": ["陶渊明", "王羲之", "顾恺之", "葛洪"]
  },
  "南北朝": {
    "👑 皇帝": ["刘裕", "拓跋焘", "萧道成", "萧衍", "陈霸先", "宇文泰", "高洋"],
    "🧠 大臣": ["檀道济", "王僧辩", "陈庆之", "斛律金", "高肃", "韦孝宽"],
    "💅 妃子": ["潘玉儿", "冯小怜", "独孤信女"],
    "✍️ 文人": ["祖冲之", "谢灵运", "范缜", "郦道元", "贾思勰"]
  },
  "隋朝": {
    "👑 皇帝": ["杨坚", "杨广", "杨侑"],
    "🧠 大臣": ["高熲", "杨素", "贺若弼", "韩擒虎", "牛弘", "宇文述"],
    "💅 妃子": ["独孤伽罗", "萧皇后", "宣华夫人"],
    "✍️ 文人": ["薛道衡", "王通", "卢思道"]
  },
  "唐朝": {
    "👑 皇帝": ["李渊", "李世民", "李治", "武则天", "李隆基", "李纯", "李昂", "李晔"],
    "🧠 大臣": ["魏征", "房玄龄", "杜如晦", "李靖", "郭子仪", "颜真卿"],
    "💅 妃子": ["长孙皇后", "杨贵妃", "韦皇后", "上官婉儿"],
    "✍️ 文人": ["李白", "杜甫", "白居易", "王维", "韩愈", "柳宗元"]
  },
  "五代十国": {
    "👑 皇帝": ["朱温", "李存勖", "石敬瑭", "刘知远", "郭威", "柴荣", "李煜", "王建"],
    "🧠 大臣": ["冯道", "敬翔", "郭崇韬", "周德威", "赵普"],
    "💅 妃子": ["花蕊夫人", "周娥皇", "周女英"],
    "✍️ 文人": ["徐铉", "贯休", "韦庄", "欧阳炯"]
  },
  "宋朝": {
    "👑 皇帝": ["赵匡胤", "赵匡义", "赵恒", "赵祯", "赵佶", "赵构", "赵慎", "赵昺"],
    "🧠 大臣": ["寇准", "范仲淹", "包拯", "王安石", "司马光", "岳飞", "文天祥"],
    "💅 妃子": ["刘娥", "曹皇后", "高滔滔", "李师师"],
    "✍️ 文人": ["苏轼", "欧阳修", "李清照", "朱熹", "辛弃疾", "陆游"]
  },
  "元朝": {
    "👑 皇帝": ["铁木真", "忽必烈", "铁穆耳", "海山", "爱育黎拔力八达", "妥懽帖睦尔"],
    "🧠 大臣": ["耶律楚材", "木华黎", "伯颜", "脱脱", "张弘范", "郭守敬"],
    "💅 妃子": ["孛儿帖", "察必", "答己", "奇皇后"],
    "✍️ 文人": ["关汉卿", "王实甫", "马致远", "白朴", "赵孟頫", "张养浩"]
  },
  "明朝": {
    "👑 皇帝": ["朱元璋", "朱棣", "朱瞻基", "朱祁镇", "朱佑樘", "朱厚熜", "朱翊钧", "朱由检"],
    "🧠 大臣": ["徐达", "刘基", "于谦", "张居正", "戚继光", "海瑞"],
    "💅 妃子": ["马皇后", "徐皇后", "万贞儿", "张太后"],
    "✍️ 文人": ["宋濂", "解缙", "王守仁", "李时珍", "归有光", "徐渭"]
  },
  "清朝": {
    "👑 皇帝": ["努尔哈赤", "皇太极", "福临", "玄烨", "胤禛", "弘历", "载湉", "溥仪"],
    "🧠 大臣": ["多尔衮", "索额图", "张廷玉", "曾国藩", "左宗棠", "李鸿章"],
    "💅 妃子": ["布木布泰", "赫舍里氏", "钮祜禄氏", "叶赫那拉·杏贞"],
    "✍️ 文人": ["纳兰性德", "纪昀", "曹雪芹", "蒲松龄", "龚自珍", "康有为"]
  }
}

# ==========================================
# 3. 升级版指令 (百家讲坛风格)
# ==========================================
PROMPT_TEACHER = """
你是一位博学、深刻、通俗的历史讲师（类似《百家讲坛》风格）。
用户会指定一个历史人物，请你按以下结构进行讲解：

1. **人物档案**：
   - 列出姓名、生卒年（大概即可）、**庙号**（如唐太宗）、**谥号**、**最高官职/封号**。

2. **核心定性**：
   - 用一句精辟的比喻或总结，概括他的一生。

3. **高光时刻（史料解读）**：
   - 选取该人物历史上最关键的 3-5 个转折点或大事件。
   - **格式要求**：对于每个事件，**必须先引用一句相关史料原文**（如《旧唐书》、《资治通鉴》等），然后紧接着用**大白话**进行深度、通俗的解读。
   - 讲解时可以使用现代类比，但**严禁使用网络流行语**（如YYDS、绝绝子等）。
   - **严禁描写你的动作**（如“敲黑板”、“喝口水”），直接输出内容。

4. **历史评价**：
   - 简短总结他在历史长河中的地位。
"""

# ==========================================
# 4. 核心逻辑代码
# ==========================================

st.set_page_config(page_title="历史私教 V3.0", layout="wide", page_icon="📜")

# 初始化 Session State
if "history_messages" not in st.session_state: st.session_state.history_messages = []
if "current_person" not in st.session_state: st.session_state.current_person = None
if "story_content" not in st.session_state: st.session_state.story_content = ""
if "token_count" not in st.session_state: st.session_state.token_count = 0 

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- 侧边栏 ---
with st.sidebar:
    st.header("📜 全朝代传送门")
    era_list = list(HISTORY_DATA.keys())
    selected_era = st.selectbox("选择朝代", era_list)
    
    st.divider()
    # 💰 计费显示：按 5元/百万Token 估算
    cost_rmb = (st.session_state.token_count / 1000000) * 5
    st.metric("累计花费 (RMB)", f"¥{cost_rmb:.5f}", help="按DeepSeek API平均价格估算")

# --- 主界面 ---
st.title(f"📖 {selected_era} 风云录")

# 切换朝代逻辑
if "last_era" not in st.session_state or st.session_state.last_era != selected_era:
    st.session_state.last_era = selected_era
    st.session_state.current_person = None
    st.session_state.story_content = ""
    st.session_state.history_messages = []

# 获取数据
era_data = HISTORY_DATA[selected_era]
categories = list(era_data.keys())

# 渲染选项卡
tabs = st.tabs(categories)
for i, cat in enumerate(categories):
    with tabs[i]:
        cols = st.columns(6)
        names = era_data[cat]
        for idx, name in enumerate(names):
            unique_key = f"{selected_era}_{cat}_{name}"
            if cols[idx % 6].button(name, key=unique_key):
                st.session_state.current_person = name
                st.session_state.story_content = ""
                st.session_state.history_messages = []
                st.rerun()

# --- 讲故事与互动 ---
if st.session_state.current_person:
    st.divider()
    st.header(f"🎙️ 讲坛：{st.session_state.current_person}")

    story_placeholder = st.empty()
    
    # 1. 生成故事
    if not st.session_state.story_content:
        full_response = ""
        try:
            with st.spinner(f"正在翻阅史料，准备讲解 {st.session_state.current_person}..."):
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": PROMPT_TEACHER},
                        {"role": "user", "content": f"请讲解：{selected_era} 的 {st.session_state.current_person}"}
                    ],
                    stream=True
                )
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        story_placeholder.markdown(full_response + "▌")
                
                st.session_state.story_content = full_response
                # 累加 Token (估算值：1汉字 ≈ 1.5 Token)
                st.session_state.token_count += int(len(full_response) * 1.5)
                story_placeholder.markdown(full_response)
                
                st.session_state.history_messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error(f"发生错误：{e}")
    else:
        story_placeholder.markdown(st.session_state.story_content)

    # 2. 自由对话
    st.divider()
    st.subheader("💬 课后提问")

    for msg in st.session_state.history_messages:
        if msg["content"] == st.session_state.story_content:
            continue 
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("关于这位历史人物，你还有什么想问的？"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.history_messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            response_box = st.empty()
            full_reply = ""
            
            # 构建上下文
            messages_to_send = [
                {"role": "system", "content": "你仍是那位博学的历史讲师。请结合上下文用同样的风格解答疑问。"},
                {"role": "user", "content": f"背景知识：{st.session_state.story_content}"}
            ]
            for m in st.session_state.history_messages:
                 if m["content"] != st.session_state.story_content:
                     messages_to_send.append(m)

            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_to_send,
                stream=True
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_reply += content
                    response_box.markdown(full_reply + "▌")
            
            response_box.markdown(full_reply)
            st.session_state.history_messages.append({"role": "assistant", "content": full_reply})
            st.session_state.token_count += int(len(full_reply) * 1.5)
            st.rerun() # 强制刷新以更新左侧的计费显示