with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# 删顶部导航游戏按钮
html = re.sub(r'\s*<button class="ctab ctab-games"[^>]*>.*?</button>', '', html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("完成")
