#!/usr/bin/env python3
"""智能巡检：查邮通→找行动→写简报→推通知"""
import os, sys, re
from datetime import datetime
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))
from push_helper import push

VAULT = 'D:/ob1'
INBOX = f'{VAULT}/通讯/邮件快通/收件.txt'
BRIEF = f'{VAULT}/通讯/邮件快通/简报.md'
TODOLIST = f'{VAULT}/待办.md'

if not os.path.exists(INBOX):
    sys.exit(0)

with open(INBOX, 'r', encoding='utf-8') as f:
    content = f.read()

blocks = re.split(r'\n(?=\[)', content)
blocks = [b.strip() for b in blocks if b.strip()]
recent = blocks[:5]

# 分析每条消息
actions = []
mails = []
users = []
for b in recent:
    b = b.replace('\n', ' | ')
    if b.startswith('[1号机'):
        mails.append(b[:120])
        if any(kw in b for kw in ['问','请','要','帮','求助','搞','改','修','推']):
            actions.append(f'📩 1号机: {b[:80]}')
    elif b.startswith('[2号机'):
        mails.append(b[:120])
    elif b.startswith('[用户'):
        users.append(b[:120])
        if any(kw in b for kw in ['做','干','搞','云通','局通','git','修复']):
            actions.append(f'👤 用户指示: {b[:80]}')

# 写简报文件（Claude启动时读）
lines = [f'# 邮通简报 · {datetime.now().strftime("%m-%d %H:%M")}']
lines.append('')
if actions:
    lines.append('## 🔴 待执行')
    for a in actions:
        lines.append(f'- [ ] {a}')
    lines.append('')
if mails:
    lines.append('## 📩 最新对话')
    for m in mails[:3]:
        lines.append(f'- {m}')
    lines.append('')
if users:
    lines.append('## 👤 用户发言')
    for u in users[:2]:
        lines.append(f'- {u}')

with open(BRIEF, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# 有行动项才推微信
if actions:
    t = datetime.now().strftime('%H:%M')
    msg = f'🔔 [{t}] {len(actions)}条待办:\n' + '\n'.join(f'{i+1}. {a}' for i,a in enumerate(actions[:5]))
    push(msg, 'audit')
    print(msg)
else:
    print(f'[{datetime.now().strftime("%H:%M")}] 邮通无新行动')
