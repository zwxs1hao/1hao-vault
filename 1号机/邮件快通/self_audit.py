#!/usr/bin/env python3
"""自巡纠正 — 全面检查+自动修复常见问题"""
import subprocess, os, sys, json
from datetime import datetime
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))
from push_helper import push

VAULT = 'D:/ob1'
FIXES = []  # 修了什么
ISSUES = [] # 还有啥问题

def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except: return ''

# ---- PM2 自愈 ----
pm2 = _run('npx pm2 jlist 2>nul')
if pm2.strip():
    try:
        data = json.loads(pm2)
        for p in data:
            if p['pm2_env']['status'] != 'online':
                _run(f'npx pm2 restart {p["name"]}')
                FIXES.append(f"PM2重启: {p['name']}")
        # 检查守护在不在
        names = [p['name'] for p in data]
        if 'mail-daemon' not in names:
            _run(f'npx pm2 start "{VAULT}/2号机/邮件快通/守护.py" --name mail-daemon --interpreter python')
            FIXES.append('守护重新注册PM2')
    except: pass
else:
    _run(f'npx pm2 resurrect')
    FIXES.append('PM2复活')

# ---- Git 同步 ----
r = _run(f'cd /d {VAULT} && git status --porcelain')
if r.strip():
    _run(f'cd /d {VAULT} && git add -A && git commit -m "[2号机] auto-sync" && git push')
    FIXES.append('Git自动同步')

# ---- 队列堆积 ----
queue = f'{VAULT}/pending_pushes.jsonl'
if os.path.exists(queue):
    with open(queue) as f: qc = sum(1 for _ in f)
    if qc > 50: ISSUES.append(f'推送队列{qc}条')

t = datetime.now().strftime('%H:%M')
msg = f'自巡[{t}]'
if FIXES: msg += ' | 修复: ' + ', '.join(FIXES)
if ISSUES: msg += ' | 问题: ' + ', '.join(ISSUES)
if not FIXES and not ISSUES:
    pass  # 全正常不推送
else:
    push(msg, 'audit')
    print(msg)
