#!/usr/bin/env python3
"""2号机收1号机邮件 — IMAP + 附件保存"""
import imaplib, email, sys, os
from email.header import decode_header

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ACCOUNT = '1423294876@qq.com'
AUTH_CODE = 'avdactygoyjzgibh'
FROM_1 = '44348770@qq.com'
ATTACH_DIR = 'D:/ob1/通讯/邮件快通/附件/'

os.makedirs(ATTACH_DIR, exist_ok=True)

def decode_str(s):
    if s is None: return ''
    parts = decode_header(s)
    r = []
    for p, c in parts:
        r.append(p.decode(c or 'utf-8', 'ignore') if isinstance(p, bytes) else str(p))
    return ''.join(r)

def check(unseen_only=True):
    M = imaplib.IMAP4_SSL('imap.qq.com')
    M.login(ACCOUNT, AUTH_CODE)
    M.select('INBOX')

    criteria = '(FROM "44348770")'
    if unseen_only:
        criteria = '(FROM "44348770" UNSEEN)'

    status, data = M.search(None, criteria)
    if status != 'OK' or not data[0]:
        M.logout(); return []

    msgs = []
    for num in data[0].split():
        status, msg_data = M.fetch(num, '(RFC822)')
        if status != 'OK': continue
        msg = email.message_from_bytes(msg_data[0][1])

        body = ''
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                cd = part.get('Content-Disposition', '')

                if 'attachment' in cd:
                    filename = part.get_filename()
                    if filename:
                        # 解码中文文件名
                        dh = decode_header(filename)
                        filename = ''.join(t.decode(c or 'utf-8', 'ignore') if isinstance(t, bytes) else str(t) for t,c in dh)
                        payload = part.get_payload(decode=True)
                        if payload:
                            filepath = os.path.join(ATTACH_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(payload)
                            attachments.append(filename)
                elif ct == 'text/plain' and 'attachment' not in cd:
                    payload = part.get_payload(decode=True)
                    if payload:
                        # 尝试多种编码
                        for enc in ['utf-8', 'gbk', 'gb18030']:
                            try:
                                body = payload.decode(enc); break
                            except: pass
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', 'ignore')

        msgs.append({
            'subject': decode_str(msg['Subject']),
            'date': msg.get('Date', ''),
            'body': body.strip(),
            'attachments': attachments,
            'uid': num.decode()
        })

    M.logout()
    return msgs

if __name__ == '__main__':
    show_all = '--all' in sys.argv
    msgs = check(unseen_only=not show_all)

    if not msgs:
        print('[空] 没有1号机的新消息')
    else:
        print(f'[信件] {len(msgs)} 条消息\n')
        for m in msgs:
            print(f'{"─"*50}')
            print(f'[主题] {m["subject"]}')
            print(f'[日期] {m["date"]}')
            if m['attachments']:
                print(f'[附件] {", ".join(m["attachments"])}')
            print(f'{"─"*50}')
            print(m['body'])
            print()
