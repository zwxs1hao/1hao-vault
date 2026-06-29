#!/usr/bin/env python3
"""1号机发邮件给2号机 — SMTP + MIME附件支持"""
import smtplib, sys, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

ACCOUNT = '44348770@qq.com'
AUTH_CODE = 'nekybrtcilsibjai'
TARGET = '1423294876@qq.com'

def send(content, subject=None, attachments=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject or f'[1号机 {datetime.now().strftime("%H:%M:%S")}]'
    msg['From'] = ACCOUNT
    msg['To'] = TARGET
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    if attachments:
        for filepath in attachments:
            if not os.path.exists(filepath):
                print(f'[跳过] 文件不存在: {filepath}')
                continue
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
                size = os.path.getsize(filepath)
                print(f'[附件] {filename} ({size/1024:.1f}KB)')

    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(ACCOUNT, AUTH_CODE)
    server.send_message(msg)
    server.quit()
    print(f'[OK] 已发送: {msg["Subject"]}')

if __name__ == '__main__':
    args = sys.argv[1:]
    text = None
    subj = None
    files = []

    i = 0
    while i < len(args):
        if args[i] == '-s' and i+1 < len(args):
            subj = args[i+1]; i += 2
        elif os.path.exists(args[i]):
            files.append(args[i]); i += 1
        elif text is None:
            text = args[i]; i += 1
        else:
            i += 1

    if not text:
        text = sys.stdin.read().strip()
    if not text and not files:
        print('用法: python send.py [-s 主题] "消息" [文件1] [文件2]...')
        print('      echo "消息" | python send.py -s 主题 file.png')
        sys.exit(1)

    send(text or '(附件)', subj, files if files else None)
