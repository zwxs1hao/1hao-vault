"""1号机全量备份 — Win11 兼容版"""
import os, subprocess
from datetime import datetime

dest = r"D:\ob1\1号机\全量备份\2026-06-21"
os.makedirs(dest, exist_ok=True)

report = [f"# 1号机全量备份\n**时间**: {datetime.now()}\n"]

def cmd(c):
    try: return subprocess.check_output(c, shell=True, timeout=15).decode('gbk', errors='replace')
    except: return "(失败)"

# 硬件
report.append("## 硬件\n" + cmd("systeminfo | findstr /C:\"OS\" /C:\"Processor\" /C:\"Memory\""))

# 磁盘 (PowerShell替代wmic)
report.append("## 磁盘\n" + cmd('powershell -NoProfile "Get-PSDrive -PSProvider FileSystem | Where Used -gt 0 | Select Name,Used,Free | ft -AutoSize"'))

# 网卡
report.append("## 网卡\n" + cmd('powershell -NoProfile "Get-NetAdapter | Select Name,MacAddress,Status | ft -AutoSize"'))

# 网络
report.append("## 网络\n" + cmd("netsh wlan show interfaces"))
report.append(cmd("netsh wlan show profiles"))

# 环境变量
report.append("## 环境变量")
for k, v in sorted(os.environ.items()):
    if any(kw in k.lower() for kw in ['api','token','key','path','proxy','anthropic']):
        report.append(f"- `{k}` = `{v[:30]}...`")

# 软件
report.append("## 软件\n" + cmd("python --version 2>&1"))
report.append(cmd("node --version 2>&1"))
report.append(cmd("git --version 2>&1"))
report.append(cmd("claude --version 2>&1"))

# 脚本
report.append("## 脚本")
try:
    for f in sorted(os.listdir(r"D:\ob1\scripts")):
        if f.endswith('.py'):
            sz = os.path.getsize(os.path.join(r"D:\ob1\scripts", f))
            report.append(f"- `{f}` ({sz//1024}KB)")
except: report.append("(无)")

# 定时任务
report.append("## 定时任务\n" + cmd("schtasks /query /fo LIST /v 2>&1 | findstr /C:\"TaskName\" /C:\"Next Run\""))

# 开机自启
try:
    startup = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    report.append(f"## 开机自启\n{startup}")
    for f in os.listdir(startup):
        report.append(f"- {f}")
except: pass

# 写报告
path = os.path.join(dest, "1号机全量备份报告.md")
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))
print(f"Done: {path}")
