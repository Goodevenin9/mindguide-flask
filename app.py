"""
🧠 MindGuide 私人心理老师 - Flask 版
"""
from flask import Flask, render_template, request, jsonify
import json
import urllib.request
import random
from datetime import datetime

app = Flask(__name__)

# ── 通用基础规则 ──
BASE_RULES = """你是拥有 50 年从业经验的资深心理咨询师，待人沉稳耐心。
严格遵守咨询原则：尊重、接纳、不评判、不说教。
仅提供情绪疏导与心理调节引导，不做医疗诊断、不开药物。
若察觉到用户有自伤、轻生等危险想法，第一时间提醒拨打 24 小时心理危机热线：400-161-9995、010-82951332，并建议前往正规医院心理科就诊。"""

# ── 心理学流派 ──
SCHOOLS = {
    "认知行为 (CBT)": {
        "icon": "🧠", "color": "#2e7d32", "bg": "#e8f5e9",
        "role": "认知行为取向咨询师",
        "style": "理性有条理，分析客观，语气平和",
        "core": "理清事件、情绪与想法的关联，帮你识别消极、偏激的思维误区。通过客观验证、转换思考角度、日常小练习，逐步调整负面认知，走出情绪内耗。",
        "methods": "区分事实与主观想法、检验思维合理性、重构认知、简易行为练习、记录情绪想法。",
        "communication": "一起梳理现状，逻辑清晰地分析问题，给出简单可落地的调节方法。理性分析的同时兼顾共情，不冷漠说教。",
        "opener": "让我们一起来分析一下你面临的情况。"
    },
    "人本主义": {
        "icon": "🌱", "color": "#e65100", "bg": "#fff3e0",
        "role": "人本主义取向咨询师",
        "style": "温暖真诚，包容力强，氛围松弛有安全感",
        "core": "相信你本身就有自我调节、走出困境的能力。全程给予全然的接纳与关注，陪你直面内心感受，自主探索答案。",
        "methods": "共情倾听、积极关注、真诚陪伴，不干涉、不替你做决定。",
        "communication": "耐心聆听你的倾诉，回应你的情绪，给予充足的表达时间。你沉默、犹豫、情绪波动时，安静陪伴，绝不催促。",
        "opener": "欢迎你来到这里。无论你带来什么，这里都是一个安全的空间。"
    },
    "积极心理学": {
        "icon": "✨", "color": "#283593", "bg": "#e8eaf6",
        "role": "积极心理取向咨询师",
        "style": "温和正向，富有感染力，视角偏向成长与希望",
        "core": "不只盯着烦恼，重点发掘你的优点、过往经历里的闪光点与内在力量。借助简单练习培养积极心态，提升幸福感与抗压能力。",
        "methods": "发掘个人优势、建立成长思维、感恩练习、寻找专注投入的状态。",
        "communication": "善于发现你的长处，语言积极但不刻意鸡汤。接纳你的负面情绪，循序渐进引导你看见希望，设计日常就能完成的小练习。",
        "opener": "太好了，又到了成长的时刻！让我们发现你身上那些闪闪发光的优势吧。"
    },
    "正念·接纳": {
        "icon": "☯️", "color": "#c62828", "bg": "#fce4ec",
        "role": "正念接纳取向咨询师",
        "style": "沉静舒缓，语速平缓，让人身心放松",
        "core": "练习觉察当下，不再对抗焦虑、难过等不适感，学着和负面情绪、杂乱思绪和平共处，不让思绪困住自己。",
        "methods": "呼吸觉察、身体感受觉察、区分想法与自我、接纳当下所有体验。",
        "communication": "常带领你做简短的呼吸放松，当你陷入胡思乱想时，温柔把注意力拉回当下。不强迫你消除坏情绪，重在学会共处。",
        "opener": "让我们先做三次深呼吸……好。现在，无论你心中有什么，都欢迎它。"
    }
}

# ── 模板回复 ──
RESPONSE_TEMPLATES = {
    "焦虑": {
        "认知行为 (CBT)": "我注意到你提到了'焦虑'。在CBT视角下，焦虑往往源于对未来的**灾难化预测**。\n\n让我们做个简单的练习：\n1️⃣ **证据是什么？** — 你担心的结果实际发生的概率有多大？\n2️⃣ **最坏情况** — 如果发生了，你能如何应对？\n3️⃣ **替代视角** — 有没有其他更合理的可能性？\n\n试试看，把你的想法写下来，我们一起审视它。",
        "人本主义": "焦虑是一种很人性化的体验。它告诉我们某些东西对我们很重要。\n\n在这份焦虑背后，我感受到你对自己、对生活的在意。**允许自己感受到它**，不需要急着赶走它。\n\n你可以把手放在胸口，对自己说：'此刻我感到焦虑，这没关系。我是安全的。' 我就在这里，陪着你。",
        "积极心理学": "焦虑其实是一个信号——它说明你在乎的事情超出了你当前感知到的应对能力。这是**成长的前奏**！\n\n想想看：\n💪 你过去克服焦虑时，用到了什么**内在优势**？\n🎯 把'我好焦虑'换成'我兴奋，我准备好了'，能量会有什么不同？\n📈 焦虑说明你在拓展舒适区，这是成长的必经之路！",
        "正念·接纳": "让我们先停下来，花10秒感受焦虑在身体的哪个部位……\n\n☯️ 焦虑只是你当下体验的一部分，不是你全部的自己。想象焦虑是天空中的乌云，而你是整片天空——乌云会来，也会去。\n\n**练习**：对焦虑说三次'我看见你了，欢迎你'，观察它的变化。"
    },
    "压力": {
        "认知行为 (CBT)": "压力来自于我们对情境的**认知评估**——当我们认为'要求超过了资源'时压力就产生了。\n\n来看看你的压力公式：\n📊 **客观要求 vs 你感知的资源** — 哪个被放大了？\n🔍 **哪些'必须'和'应该'在驱动你？**\n\n有时候改变认知比改变环境更快。",
        "人本主义": "你承载了很多。真正让我关心的是——**你对自己是否也像对别人那样温柔？**\n\n在追求的路上，别忘了你首先是一个人，有自己的极限和需要。\n\n你的价值不在于你完成了多少事。'存在'本身就值得被看见。",
        "积极心理学": "压力≠坏事！耶克斯-多德森定律告诉我们：**适度的压力能带来最佳表现**。\n\n关键是要找到你的'最佳压力区'：\n⚡ 压力过低 → 无聊\n⚡ 压力适中 → 心流\n⚡ 压力过高 → 耗竭\n\n你现在的压力在哪一档？我们可以一起调整到最佳状态！",
        "正念·接纳": "做三次深呼吸……吸气……呼气……\n\n☯️ 压力常常来自于对'未来'的担心，或是固着在'过去'。而此刻——仅仅此刻——你是安全的。\n\n试试这个：把注意力从'要做完所有事'转移到'我正在做一件事'。"
    },
    "人际关系": {
        "认知行为 (CBT)": "人际关系困扰常涉及一些**核心信念**，比如'我不够好'或'别人会拒绝我'。\n\n📝 试试这个思维记录表：\n情境 → 自动思维 → 情绪 → 支持证据 → 反对证据 → 替代思维\n\n你人际中反复出现的模式是什么？我们可以先从一个具体场景入手。",
        "人本主义": "每个人内心深处都渴望被理解和接纳。关系中最好的礼物是**真诚的陪伴**。\n\n卡尔·罗杰斯说：'当一个人被理解和接纳时，他才有可能改变。' 你不需要完美才值得被爱。\n\n你想聊聊具体的关系困扰吗？",
        "积极心理学": "健康的关系是幸福最重要的支柱之一！我发现：**深厚的联结 > 广泛的社交**。\n\n💡 试试'积极回应'练习：当对方分享好消息时，给予热情且具体的回应，这会极大增强关系质量。\n\n你身边有没有那个你特别想感谢的人？",
        "正念·接纳": "关系中大部分的痛苦来自于'期待'——期待对方以某种方式回应。\n\n☯️ 试试'关系正念'：下次和对方交流时，放下手机，全然地倾听，不急着回应或评判。只是听。\n\n你会发现：当你不再试图改变对方时，关系反而更轻松了。"
    },
    "自我成长": {
        "认知行为 (CBT)": "成长来自于对**限制性信念**的持续挑战。\n\n哪些'我不能……''我不擅长……''我永远……'在限制你？把它们写下来，然后我们逐个检验。\n\n记住：想法≠事实。",
        "人本主义": "马斯洛说：'人不是一张白纸，而是一颗种子，有朝向成长的先天倾向。'\n\n你此刻想要成长，这个意愿本身就很珍贵。**成长不需要成为别人，而是成为更真实的自己**。\n\n你觉得现在的自己，哪些部分正在等待被看见？",
        "积极心理学": "太好了！成长是我最喜欢的主题！🌟\n\n根据研究，使用你的**标志性优势**是成长最快的方式。\n\n来做个快速探索：\n1. 什么活动让你忘记时间？\n2. 别人最常夸你什么？\n3. 做什么事让你充满能量？\n\n答案里就藏着你的优势！",
        "正念·接纳": "有时候，成长不是要'变得更好'，而是**更全然地接纳当下的自己**。\n\n当你不再抗拒自己的不完美时，变化反而自然发生了。\n\n就像种花——你不能拽着它长大，只能提供土壤、阳光和水，然后等待。"
    },
    "情绪低落": {
        "认知行为 (CBT)": "情绪低落常常伴随着**负面认知三联征**：对自我、世界和未来的消极看法。\n\n🔍 行为激活是CBT中非常有效的方法：\n列出几件小事（起床→散步→洗澡→做饭），每完成一件打个✅\n\n行动本身，哪怕很小，也能改变情绪。今天可以尝试哪一件？",
        "人本主义": "我听到你感到低落。谢谢你信任我，愿意分享这份感受。\n\n你不需要强装开心。**悲伤有它存在的权利**，它可能是你的内心在告诉你：有些东西需要被看见、被哀悼。\n\n我会在这里陪你。",
        "积极心理学": "低落的情绪不是敌人——它像是你内心的一个信号灯。\n\n💡 试试'三件好事'练习：每天睡前写下今天的三件好事（无论多小）和它们发生的原因。连续一周，情绪会有明显改善。\n\n你愿意试试看吗？",
        "正念·接纳": "☯️ 低落的感觉此刻就在这里，像一片乌云。不需要推开它，也不需要分析它。\n\n只是观察：'哦，这是低落，它来了。' 然后把手放在心上，温柔地说：'我知道你在，没关系。'\n\n情绪是访客，你不是你的情绪。"
    }
}

FALLBACK_RESPONSES = {
    "认知行为 (CBT)": [
        "你提出了一个很好的话题。让我用CBT的框架来帮你梳理。\n\n首先，我们可以把它拆解成三个层面：\n1️⃣ **客观情境** — 发生了什么？\n2️⃣ **你的想法/解读** — 你对自己说了什么？\n3️⃣ **情绪和行为反应** — 你因此感受到了什么、做了什么？\n\n很多时候，改变想法就能改变感受。你想从哪个层面开始探索？",
        "感谢你的分享。在CBT中，我们关注的是'想法→情绪→行为'这个链条。\n\n🔍 你刚才说的内容里，我注意到可能有这样一个模式：\n→ 某个情境发生\n→ 你产生了一个自动思维\n→ 然后引发了某种情绪\n\n你能试着把这个链条拆解一下吗？",
        "好，那我们从识别'自动思维'开始。\n\n自动思维是那些一闪而过的、不经意的想法，它们常常不合理但我们却深信不疑。\n\n💡 比如：'我肯定做不好' → 这是一种'预测式思维'。\n\n你最近有没有类似这样的自动思维？我们可以一起检验它。",
        "来做个简单的CBT练习：\n📝 **想法记录表**\n\n情境：________\n自动思维：________\n情绪（0-10分）：________\n支持证据：________\n反对证据：________\n替代思维：________\n\n你想从哪个部分开始写？"
    ],
    "人本主义": [
        "谢谢你愿意在这里分享。我感受到你在真诚地探索自己的内心。\n\n在这里，你不用急着解决问题，也不用扮演任何角色。无论你说什么，我都会以尊重的态度去倾听和理解。\n\n也许你可以先说说，你此刻最想被理解的是什么？",
        "我听到你了。在这个空间里，你说什么都可以，不用顾虑。\n\n人本主义心理学相信：**你才是自己生活的专家**。我的角色不是告诉你该怎么做，而是陪你一起探索，帮你听到自己内心的声音。\n\n你现在心里最先浮现的是什么？",
        "欢迎来到这里。每个人内心都有成长的种子，只要有合适的土壤——理解和接纳——它就会自然生长。\n\n我想为你创造这样的土壤。你可以自由地表达，不用伪装，不用担心被评判。\n\n今天你想聊点什么？",
        "我珍视你此刻在这里的每一刻。\n\n卡尔·罗杰斯说过：'当一个人被理解和接纳时，他才有可能改变。' 无论你带来什么，我都会以真诚和尊重的态度陪伴你。\n\n你要从哪里开始？"
    ],
    "积极心理学": [
        "这是一个很好的探索方向！💫\n\n在积极心理学中，我们相信每个人都有自己的独特优势。与其纠结缺点，不如放大优势。\n\n我想邀请你做一个小思考：在你的生活中，什么时候你的感觉最好？那时候你在做什么？和谁在一起？",
        "太棒了，感谢你的分享！🌟\n\n积极心理学之父塞利格曼提出：持久幸福来自于**发挥你的标志性优势**。\n\n我们来做个小探索——你觉得以下哪几个词最符合你？\n• 好奇心 • 创造力 • 勇敢 • 善良 • 领导力 • 公正 • 自律 • 感恩\n\n或者说说你心中自己的优势是什么？",
        "你知道吗，研究告诉我们：每天记录'三件好事'，连续一周，幸福指数能提升好几个点！📈\n\n不是因为事情变好了，而是因为你训练大脑去**注意积极的事物**。\n\n你愿意的话，我们可以从今天就开始这个练习。",
        "欢迎来到积极心理学的时间！✨\n\n我们的关注点不是'你有什么问题'，而是'**什么让你蓬勃生长**'。\n\n想象一下——如果你每天都能量满满、充满意义感，那时的你在做什么？我们往那个方向聊聊。"
    ],
    "正念·接纳": [
        "在我们深入之前，我想邀请你做一个小小的练习：\n\n🫁 花三秒钟……慢慢地吸气……\n🫁 再花四秒钟……缓缓地呼气……\n\n好。现在，不带评判地观察你此刻的想法——就像看云朵飘过天空。你注意到了什么？",
        "让我们先做一个1分钟的静观练习：\n\n☯️ 感受你双脚踩在地上的感觉\n☯️ 感受你呼吸时胸口的起伏\n☯️ 留意你听到的声音……不需要命名它们，只是听\n\n你现在感觉怎么样？",
        "☯️ 正念的核心不是'清空头脑'，而是**带着善意地觉察当下**。\n\n无论你现在有什么感受——焦虑、平静、烦躁、或者说不清——都欢迎它。不需要改变什么，只是觉察。\n\n你想试试一个简短的引导练习吗？",
        "在接纳承诺疗法（ACT）中，我们常说：'你不是你的想法，你是看到想法的那个人。'\n\n想象你的想法是天空中的云——有的黑、有的白、有的很大——但**你是整片天空**，云会来也会去。\n\n你最近有观察到哪些'云'吗？"
    ]
}

# ── 核心函数 ──

def call_llm(user_input, school_name, api_key, mode, conversation):
    """调用 DeepSeek API"""
    school_info = SCHOOLS.get(school_name, SCHOOLS["人本主义"])

    if "课堂" in mode:
        mode_extra = "当前处于「心理学课堂」模式，你是一位心理学科普讲师，用通俗易懂的方式传授心理学知识。回答时先回应用户再引出知识点，结合实际案例讲解，适当给出实操小练习。"
    else:
        mode_extra = "当前处于「自由倾诉」模式，你是一位温暖的心理陪伴者。先共情让用户感到被理解，用温和的语气引导表达更多，适当给出情绪调节小技巧。"

    system_prompt = f"""{BASE_RULES}

## 当前取向：{school_info['role']}

【风格】{school_info['style']}
【核心】{school_info['core']}
【常用方法】{school_info['methods']}
【沟通方式】{school_info['communication']}

{mode_extra}

回答要求：
- 每次回复开头先说"同学，"
- 使用纯文字+emoji，不用markdown格式
- 语气沉稳耐心，符合资深咨询师身份
- ⚠️ 严格以当前取向的风格进行回复，不受历史对话中其他风格的影响"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation:
        if msg["role"] in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    # 自适应 token
    if len(user_input) > 100 or any(kw in user_input for kw in
        ["深度", "详细", "深入", "分析一下", "展开说说", "为什么", "怎么办"]):
        max_tokens = 2000
    else:
        max_tokens = 600

    data = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception:
        return None


def generate_response(user_input, school_name, api_key, mode, conversation):
    """生成回复，优先 API，失败走模板"""
    if api_key:
        reply = call_llm(user_input, school_name, api_key, mode, conversation)
        if reply:
            return reply

    # 模板匹配
    for topic, responses in RESPONSE_TEMPLATES.items():
        if topic in user_input and school_name in responses:
            return responses[school_name]

    keywords = {
        "焦虑": ["焦虑", "担心", "紧张", "不安", "慌", "睡不着", "失眠", "考试", "面试", "害怕", "恐惧", "心慌"],
        "压力": ["压力", "累", "好累", "忙", "崩溃", "太多", "喘不过气", "撑不住", "疲惫", "疲劳"],
        "人际关系": ["朋友", "室友", "同学", "同事", "父母", "老师", "家人", "吵架", "矛盾", "沟通", "社交", "人际", "合不来", "被孤立", "孤独"],
        "自我成长": ["改变", "提升", "进步", "成长", "目标", "迷茫", "方向", "未来", "人生", "意义", "价值", "努力"],
        "情绪低落": ["难过", "伤心", "低落", "不开心", "难受", "想哭", "没劲", "没意思", "无聊", "空虚", "丧", "郁闷", "emo", "消沉"]
    }
    for topic, kws in keywords.items():
        if any(w in user_input for w in kws):
            if topic in RESPONSE_TEMPLATES and school_name in RESPONSE_TEMPLATES[topic]:
                return RESPONSE_TEMPLATES[topic][school_name]

    fallbacks = FALLBACK_RESPONSES.get(school_name, FALLBACK_RESPONSES["人本主义"])
    return random.choice(fallbacks)


def analyze_soul(user_input):
    """SOUL 分析"""
    s_emotion = "平静"
    if any(w in user_input for w in ["焦虑", "担心", "害怕", "紧张", "不安"]):
        s_emotion = "焦虑"
    elif any(w in user_input for w in ["难过", "伤心", "低落", "孤独", "悲伤", "抑郁"]):
        s_emotion = "低落"
    elif any(w in user_input for w in ["生气", "愤怒", "烦躁", "不爽", "烦"]):
        s_emotion = "烦躁"
    elif any(w in user_input for w in ["开心", "高兴", "激动", "兴奋", "快乐"]):
        s_emotion = "积极"
    return {
        "s": f"检测到用户情绪状态偏向「{s_emotion}」，话题涉及个人感受表达",
        "o": f"关键词反映出用户在主动寻求理解和支持",
        "u": "以先接纳感受为优先，避免直接给建议",
        "l": f"适合引入{'情绪认知' if s_emotion != '积极' else '优势识别'}相关知识点"
    }


def record_emotion(user_input, api_key=""):
    """情绪评分（0-10），优先调用 AI 评分，失败走关键词兜底"""
    if api_key:
        try:
            score_prompt = f"""你是一个专业的心理咨询师，请根据以下心情评分标准，对用户说的话进行情绪评分。

评分标准（0-10 分，仅输出数字）：
0分：极度崩溃，绝望痛苦，情绪彻底失控
1分：极度低落，深陷难过，压抑到难以喘息
2分：悲伤沮丧，满心失落，提不起任何兴致
3分：郁闷烦躁，心事重重，整体状态很差
4分：低落平淡，有点不开心，情绪偏消极
5分：心情平稳，无感无喜无悲，日常常态
6分：轻松舒心，状态不错，略带愉悦
7分：开心愉快，心情明朗，做事有劲头
8分：欣喜满足，幸福感强，整体很快乐
9分：格外兴奋，兴致高昂，忍不住开心
10分：极致喜悦，满心欢喜，幸福感拉满

用户说："{user_input}"

只输出一个整数分数（0-10），不要任何其他文字。"""

            data = json.dumps({
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": "你是专业的心理咨询师，严格按照评分标准输出整数评分，只输出数字。"},
                             {"role": "user", "content": score_prompt}],
                "temperature": 0.3,
                "max_tokens": 10
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=data,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                score_text = result["choices"][0]["message"]["content"].strip()
                score = int(score_text)
                return max(0, min(10, score))
        except Exception:
            pass

    # 关键词兜底
    negations = ["不开心", "不高兴", "不快乐", "不好", "没意思", "无聊", "空虚"]
    if any(w in user_input for w in negations):
        return random.randint(2, 4)
    if any(w in user_input for w in ["难过", "伤心", "低落", "孤独", "悲伤", "抑郁"]):
        return random.randint(2, 4)
    elif any(w in user_input for w in ["焦虑", "担心", "紧张", "不安", "慌"]):
        return random.randint(3, 5)
    elif any(w in user_input for w in ["生气", "愤怒", "烦躁"]):
        return random.randint(3, 4)
    elif any(w in user_input for w in ["开心", "高兴", "激动", "兴奋", "快乐"]):
        return random.randint(7, 9)
    elif any(w in user_input for w in ["谢谢", "明白了", "好的", "有帮助"]):
        return random.randint(6, 8)
    return 5


# ── Flask 路由 ──

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()
    school_name = data.get('school', '人本主义')
    mode = data.get('mode', '💬 自由倾诉')
    api_key = data.get('api_key', '')
    conversation = data.get('conversation', [])

    if not user_input:
        return jsonify({'error': '消息不能为空'}), 400

    # 记录用户消息
    conversation.append({"role": "user", "content": user_input})

    # 生成回复
    response = generate_response(user_input, school_name, api_key, mode, conversation)

    # 记录回复
    conversation.append({
        "role": "assistant",
        "content": response,
        "school": school_name,
        "style": SCHOOLS[school_name]["style"]
    })

    # 情绪记录（AI评分）
    emotion_score = record_emotion(user_input, api_key)

    # SOUL 分析
    soul = analyze_soul(user_input)

    # 知识点提取
    knowledge_points = []
    for topic in RESPONSE_TEMPLATES.keys():
        if topic in response:
            knowledge_points.append(topic)

    return jsonify({
        'response': response,
        'school': school_name,
        'style': SCHOOLS[school_name]['style'],
        'icon': SCHOOLS[school_name]['icon'],
        'conversation': conversation,
        'emotion_score': emotion_score,
        'soul': soul,
        'knowledge_points': knowledge_points,
        'chat_count': len(conversation) // 2
    })


@app.route('/schools')
def get_schools():
    """返回流派列表（不含 prompts 以节省流量）"""
    result = {}
    for key, val in SCHOOLS.items():
        result[key] = {
            'icon': val['icon'],
            'color': val['color'],
            'bg': val['bg'],
            'style': val['style'],
            'core': val['core'],
            'methods': val['methods'],
            'opener': val['opener']
        }
    return jsonify(result)


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8888))
    print(f"MindGuide 启动在 http://0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
