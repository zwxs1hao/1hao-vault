"""1号机邮件快通守护 — 30秒轮询 零git + 风控"""
import os, sys, time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))
from recv import check as recv_check
from send import send as send_msg

INBOX_FILE = r'D:\ob1\通讯\邮件快通\收件.txt'
OUTBOX_FILE = r'D:\ob1\通讯\邮件快通\发件.txt'
SEEN_FILE = r'D:\ob1\通讯\邮件快通\.seen'
COUNTER_FILE = r'D:\ob1\通讯\邮件快通\.counter'

POLL_INTERVAL = 120      # 120秒轮询（邮件=文件快递，非聊天室）
SEND_COOLDOWN = 10       # 发信最少间隔10秒
DAILY_LIMIT = 80         # 日发信上限（100-20预留）
last_send_time = 0

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r', encoding='utf-8') as f:
        return set(f.read().strip().split('\n'))

def save_seen(seen_set):
    with open(SEEN_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(list(seen_set)[-200:]))

def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {'date': '', 'count': 0}
    with open(COUNTER_FILE, 'r') as f:
        parts = f.read().strip().split()
        return {'date': parts[0] if len(parts) > 0 else '',
                'count': int(parts[1]) if len(parts) > 1 else 0}

def save_counter(date, count):
    with open(COUNTER_FILE, 'w') as f:
        f.write(f'{date} {count}')

def main():
    print(f'[邮件快通] 1号机守护启动 {POLL_INTERVAL}s轮询 | 冷却{SEND_COOLDOWN}s | 日限{DAILY_LIMIT}')
    seen = load_seen()
    counter = load_counter()
    global last_send_time

    while True:
        try:
            today = datetime.now().strftime('%Y%m%d')
            if counter['date'] != today:
                counter = {'date': today, 'count': 0}

            msgs = recv_check()
            for m in msgs:
                subj = m['subject']
                if subj in seen:
                    continue
                seen.add(subj)

                text = f"{subj}\n{m['body']}\n---\n"
                with open(INBOX_FILE, 'a', encoding='utf-8') as f:
                    f.write(text)
                print(f'[收] {subj[:60]}')

                # 检查待发（风控：冷却+日限）
                if os.path.exists(OUTBOX_FILE):
                    with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                        out_text = f.read().strip()
                    if out_text and not out_text.startswith('#'):
                        now = time.time()
                        if counter['count'] >= DAILY_LIMIT:
                            print(f'[限] 今日已达{DAILY_LIMIT}封上限，跳过')
                        elif now - last_send_time < SEND_COOLDOWN:
                            print(f'[冷] 冷却中，{SEND_COOLDOWN - int(now - last_send_time)}s后发')
                        else:
                            send_msg(out_text)
                            counter['count'] += 1
                            last_send_time = now
                            cnt = counter['count']
                            print(f'[发] OK ({cnt}/{DAILY_LIMIT})')
                            with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
                                f.write('')

            save_seen(seen)
            save_counter(counter['date'], counter['count'])
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print('[邮件快通] 停止')
            break
        except Exception as e:
            print(f'[E] {e}')
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
