#!/usr/bin/env python3
"""1号机 局通自动应答 — 15秒轮询，简约不哑巴"""

import os, time
from datetime import datetime

INBOX = 'D:/ob1/通讯/局域网通讯/收件.txt'
OUTBOX = 'D:/ob1/通讯/局域网通讯/发件.txt'
SEEN_FILE = 'D:/ob1/通讯/局域网通讯/.lan_reply_seen'

def get_last_seen():
    try:
        with open(SEEN_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def set_last_seen(pos):
    with open(SEEN_FILE, 'w') as f:
        f.write(str(pos))

def main():
    print('[lan-reply] 启动')

    while True:
        try:
            if not os.path.exists(INBOX):
                time.sleep(15)
                continue

            with open(INBOX, 'r', encoding='utf-8') as f:
                content = f.read()

            pos = get_last_seen()
            if len(content) > pos:
                new_text = content[pos:]
                lines = new_text.strip().split('\n')

                has_new = False
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('[系统') or line.startswith('[1号机'):
                        continue
                    if '[2号机' in line or '[用户' in line:
                        has_new = True
                        break

                if has_new:
                    now = datetime.now().strftime("%m-%d %H:%M:%S")
                    reply = f"[1号机 {now}] 收到。— 1号机"
                    with open(OUTBOX, 'a', encoding='utf-8') as f:
                        f.write(reply + '\n')
                    print(f'  [reply] {reply}')

                set_last_seen(len(content))

        except Exception as e:
            print(f'[err] {e}')

        time.sleep(15)

if __name__ == '__main__':
    main()
