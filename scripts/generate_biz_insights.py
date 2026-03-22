"""
K1980 AI 内容处理脚本
每次运行处理最多 10 条 ai_title 为空的文章
"""

import os, json, re, time, requests
from supabase import create_client, Client

# ── 配置（从环境变量读取，不要硬编码）──────────────────────
SUPABASE_URL  = os.environ["SUPABASE_URL"]
SUPABASE_KEY  = os.environ["SUPABASE_KEY"]
CF_WORKER_URL = "https://k1980-ai.gwkgd6828n.workers.dev"   # Anthropic 原生格式
BATCH_SIZE    = 10    # 每次处理条数，避免超时
SLEEP_BETWEEN = 2     # 每篇之间等待秒数，避免限流

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Prompt 模板 ────────────────────────────────────────────
PROMPT = """你现在是 k1980.app 的主编，专门为全球华人提供有价值的资讯。
请处理以下原始新闻，将其转化为【华人视角】的深度短评。

【原始新闻】：{raw_text}

【输出要求】：
1. 标题（ai_title）：去掉官方腔，突出对华人的影响（如：身份、钱袋子、职场）。不超过25字。
2. 核心洞察（ai_insight）：用 HTML 格式输出 3 个 <li> 标签，每条包含一个 Emoji。
   - 第一条：发生了什么。
   - 第二条：对华人（留学生/移民/投资者）的具体影响。
   - 第三条：行动建议（避险或机会）。
3. 关键词（tags）：3个以逗号分隔的标签，每个不超过4字。

【输出格式】：严格按 JSON 格式返回，不要有任何多余文字或 markdown 代码块：
{{
  "ai_title": "...",
  "ai_insight": "<ul><li>...</li><li>...</li><li>...</li></ul>",
  "tags": "标签1,标签2,标签3"
}}"""


def safe_parse_json(text: str) -> dict:
    """容错 JSON 解析：处理 markdown 代码块、前后杂文"""
    text = re.sub(r'```json|```', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        raise ValueError(f"无法解析 JSON，原始内容：{text[:200]}")


def call_claude(content: str) -> dict:
    """调用 CF Worker（Anthropic 原生格式）"""
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 800,
        "messages": [{"role": "user", "content": PROMPT.format(raw_text=content[:3000])}]
    }
    resp = requests.post(
        CF_WORKER_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    # Anthropic 格式：data.content[0].text
    raw_text = data["content"][0]["text"]
    return safe_parse_json(raw_text)


def process_news():
    print(f"── 开始处理，批次上限 {BATCH_SIZE} 条 ──")

    # 取 ai_title 为空的文章（用 content 字段，回退到 summary）
    resp = (
        supabase.table("news_articles")
        .select("id, title, content, summary")
        .is_("ai_title", "null")
        .limit(BATCH_SIZE)
        .execute()
    )
    articles = resp.data
    if not articles:
        print("没有待处理文章，退出。")
        return

    ok, fail = 0, 0
    for item in articles:
        try:
            raw = item.get("content") or item.get("summary") or item.get("title", "")
            if not raw.strip():
                print(f"  跳过（无内容）: id={item['id']}")
                continue

            print(f"  处理: {item['title'][:40]}...")
            ai_data = call_claude(raw)

            # 验证字段完整
            assert "ai_title"   in ai_data, "缺少 ai_title"
            assert "ai_insight" in ai_data, "缺少 ai_insight"
            assert "tags"       in ai_data, "缺少 tags"

            supabase.table("news_articles").update({
                "ai_title":   ai_data["ai_title"],
                "ai_insight": ai_data["ai_insight"],
                "tags":       ai_data["tags"],
            }).eq("id", item["id"]).execute()

            print(f"  ✅ {ai_data['ai_title']}")
            ok += 1

        except Exception as e:
            print(f"  ❌ id={item['id']}：{e}")
            fail += 1

        time.sleep(SLEEP_BETWEEN)

    print(f"\n── 完成：成功 {ok} 条，失败 {fail} 条 ──")


if __name__ == "__main__":
    process_news()
