#!/usr/bin/env python3
"""1号机发邮件给2号机 — SMTP直连QQ邮箱"""
import smtplib
from email.mime.text import MIMEText
import sys
from datetime import datetime

ACCOUNT = '44348770@qq.com'
AUTH_CODE = 'nekybrtcilsibjai'
TARGET = '1423294876@qq.com'

def send(content, subject=None):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject or f'【1号机 {datetime.now().strftime("%H:%M:%S")}】'
    msg['From'] = ACCOUNT
    msg['To'] = TARGET
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(ACCOUNT, AUTH_CODE)
    server.send_message(msg)
    server.quit()
    print(f'[OK] 已发送: {msg["Subject"]}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        content = sys.argv[1]
        subject = sys.argv[2] if len(sys.argv) > 2 else None
        send(content, subject)
    else:
        content = sys.stdin.read().strip()
        if content:
            send(content)
        else:
            print('用法: echo "消息" | python send.py  或  python send.py "消息" "[主题]"')
