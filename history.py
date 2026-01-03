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
# 2. 全朝代历史数据库 (V4.0 增强版)
# ==========================================
# 包含了：君王、人物、典故、语文课本
HISTORY_DATA = {
  "夏商周": { 
      # 虽然你要求不合并，但夏商周资料相对较少且课本常把先秦放一起
      # 如果你想拆，可以像下面朝代一样拆开
      "👑 君王": ["大禹", "商汤", "周武王", "周幽王", "周公旦"],
      "🧠 人物": ["姜子牙", "伊尹", "比干", "妲己", "褒姒", "老子", "孔子", "屈原"],
      "📜 典故": ["大禹治水", "酒池肉林", "烽火戏诸侯", "卧薪尝胆", "问鼎中原", "退避三舍", "围魏救赵", "负荆请罪", "图穷匕见", "纸上谈兵"],
      "📚 语文课本": ["《诗经·采薇》", "《论语》十则", "《生于忧患，死于安乐》", "《曹刿论战》", "《离骚》", "《逍遥游》", "《劝学》", "《廉颇蔺相如列传》"]
  },
  "秦朝": {
    "👑 君王": ["秦始皇", "秦二世", "子婴"],
    "🧠 人物": ["李斯", "蒙恬", "王翦", "章邯", "赵高", "荆轲(刺秦)"],
    "📜 典故": ["指鹿为马", "焚书坑儒", "博浪沙刺秦", "孟姜女哭长城"],
    "📚 语文课本": ["《过秦论》", "《谏逐客书》", "《荆轲刺秦王》"]
  },
  "西汉": {
    "👑 君王": ["刘邦", "刘盈", "刘恒", "刘启", "刘彻", "刘询"],
    "🧠 人物": ["萧何", "张良", "韩信", "霍去病", "卫青", "司马迁", "张骞", "苏武"],
    "📜 典故": ["明修栈道暗度陈仓", "成也萧何败也萧何", "金屋藏娇", "封狼居胥", "苏武牧羊", "断袖之癖"],
    "📚 语文课本": ["《鸿门宴》", "《报任安书》", "《苏武传》", "《李将军列传》"]
  },
  "东汉": {
    "👑 君王": ["刘秀", "刘庄", "刘协(汉献帝)"],
    "🧠 人物": ["班超", "张衡", "蔡伦", "华佗", "孔融"],
    "📜 典故": ["投笔从戎", "不入虎穴焉得虎子", "举案齐眉", "让梨的故事(孔融)"],
    "📚 语文课本": ["《张衡传》", "《孔雀东南飞》"]
  },
  "三国": {
    "👑 君王": ["曹操", "刘备", "孙权", "曹丕"],
    "🧠 人物": ["诸葛亮", "关羽", "张飞", "赵云", "周瑜", "司马懿", "荀彧", "吕布", "华佗"],
    "📜 典故": ["桃园三结义", "三顾茅庐", "火烧赤壁", "草船借箭", "白衣渡江", "乐不思蜀", "七步成诗", "望梅止渴", "刮目相看"],
    "📚 语文课本": ["《出师表》", "《赤壁赋》(苏轼回顾)", "《短歌行》", "《观沧海》", "《隆中对》", "《陈情表》(李密)"]
  },
  "两晋南北朝": {
    "👑 君王": ["司马炎", "司马睿", "拓跋焘", "萧衍"],
    "🧠 人物": ["谢安", "王羲之", "陶渊明", "祖冲之", "祖逖", "花木兰"],
    "📜 典故": ["闻鸡起舞", "草木皆兵", "东床快婿", "入木三分", "不为五斗米折腰"],
    "📚 语文课本": ["《归去来兮辞》", "《桃花源记》", "《兰亭集序》", "《木兰诗》", "《水经注》(选)"]
  },
  "隋朝": {
    "👑 君王": ["杨坚", "杨广"],
    "🧠 人物": ["李春(赵州桥)", "宇文恺"],
    "📜 典故": ["罄竹难书", "科举制创立"],
    "📚 语文课本": ["《赵州桥》(说明文)"]
  },
  "唐朝": {
    "👑 君王": ["李渊", "李世民", "武则天", "李隆基"],
    "🧠 人物": ["魏征", "房玄龄", "李靖", "郭子仪", "玄奘"],
    "📜 典故": ["玄武门之变", "贞观之治", "请君入瓮", "贵妃醉酒", "一骑红尘妃子笑", "安史之乱"],
    "📚 语文课本": ["《师说》", "《长恨歌》", "《琵琶行》", "《蜀道难》", "《将进酒》", "《茅屋为秋风所破歌》", "《滕王阁序》", "《阿房宫赋》", "《陋室铭》"]
  },
  "宋朝": {
    "👑 君王": ["赵匡胤", "赵光义", "赵祯", "赵佶", "赵构"],
    "🧠 人物": ["王安石", "司马光", "苏轼", "岳飞", "包拯", "文天祥", "辛弃疾", "李清照"],
    "📜 典故": ["杯酒释兵权", "狸猫换太子", "精忠报国", "莫须有", "东窗事发", "程门立雪"],
    "📚 语文课本": ["《岳阳楼记》", "《醉翁亭记》", "《赤壁赋》", "《念奴娇·赤壁怀古》", "《水调歌头》", "《声声慢》", "《永遇乐·京口北固亭怀古》", "《石钟山记》"]
  },
  "元朝": {
    "👑 君王": ["忽必烈"],
    "🧠 人物": ["关汉卿", "马致远", "郭守敬", "文天祥(抗元)"],
    "📜 典故": ["人生自古谁无死", "道路以目"],
    "📚 语文课本": ["《窦娥冤》", "《天净沙·秋思》"]
  },
  "明朝": {
    "👑 君王": ["朱元璋", "朱棣", "朱由检(崇祯)"],
    "🧠 人物": ["郑和", "于谦", "海瑞", "张居正", "戚继光", "徐霞客", "李时珍"],
    "📜 典故": ["靖难之役", "郑和下西洋", "土木堡之变", "粉身碎骨浑不怕"],
    "📚 语文课本": ["《项脊轩志》", "《送东阳马生序》", "《石灰吟》"]
  },
  "清朝": {
    "👑 君王": ["康熙", "雍正", "乾隆", "慈禧", "溥仪"],
    "🧠 人物": ["和珅", "纪晓岚", "林则徐", "曾国藩", "左宗棠", "曹雪芹", "谭嗣同"],
    "📜 典故": ["文字狱", "康乾盛世", "虎门销烟", "垂帘听政", "戊戌六君子"],
    "📚 语文课本": ["《红楼梦》(选段)", "《登泰山记》", "《病梅馆记》", "《少年中国说》"]
  }
}

# ==========================================
# 3. 智能通用指令 (V4.0 - 自动识别类型)
# ==========================================
# 这个指令让 AI 变得聪明：它会自己判断用户点的是人、故事还是课文
PROMPT_V4 = """
你是一位博学、通俗的历史与文学讲师（类似《百家讲坛》风格）。
用户会给你一个【朝代】和一个【关键词】（可能是人物、典故、或者课文标题）。
请先判断关键词的类型，然后按对应逻辑讲解：

### 情况 A：如果关键词是【历史人物】
1. **人物档案**：姓名、生卒大概年代、身份/称号。
2. **核心定性**：一句话概括他的一生。
3. **高光时刻**：列举2-3个关键事件，**引用相关史料**（如《史记》等），然后用大白话解读。

### 情况 B：如果关键词是【典故/成语/事件】（如“白衣渡江”、“指鹿为马”）
1. **典故档案**：出处（哪本书）、涉及的主角。
2. **故事还原**：用生动的语言还原当时的场景。
3. **含义与用法**：解释这个典故现在的意思，或者它说明了什么道理。

### 情况 C：如果关键词是【语文课文/文学作品】（如《出师表》、《阿房宫赋》）
1. **作品名片**：作者、体裁、创作背景（当时发生了什么）。
2. **名句赏析**：摘录文中1-2句最经典的千古名句，并解释其含义。
3. **串联知识**：**这一点最重要！** 请解释这篇课文在历史上的地位，或者它反映了当时怎样的历史现象？帮助用户把“语文知识”和“历史知识”串联起来。

**通用要求**：
- 风格通俗幽默，但引用要严谨。
- 严禁使用网络烂梗。
- 严禁描写你的动作（如“敲黑板”）。
"""

# ==========================================
# 4. 核心逻辑代码
# ==========================================

st.set_page_config(page_title="历史私教 V4.0", layout="wide", page_icon="📜")

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
categories = list(era_data.keys()) # 自动获取 [君王, 人物, 典故, 语文课本]

# 渲染选项卡 (Tabs)
# Streamlit 会根据 keys 的数量自动生成对应数量的 tab
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
            with st.spinner(f"AI 老师正在备课：{st.session_state.current_item}..."):
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
