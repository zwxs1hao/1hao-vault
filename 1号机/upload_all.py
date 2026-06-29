import base64, json, urllib.request, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'zwxs1hao/1hao-vault'
HEADERS = {'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'}
BASE = '1号机/'

total = 0
ok = 0
fail = 0

for root, dirs, files in os.walk(BASE):
    for fname in files:
        fpath = os.path.join(root, fname).replace('\\', '/')
        total += 1
        api_path = urllib.parse.quote(fpath, safe='')

        try:
            with open(fpath, 'rb') as f:
                content = base64.b64encode(f.read()).decode('ascii')
        except:
            fail += 1
            continue

        payload = json.dumps({'message': f'[1号机] add {fname}', 'content': content}).encode('utf-8')
        req = urllib.request.Request(
            f'https://api.github.com/repos/{REPO}/contents/{api_path}',
            data=payload, headers=HEADERS, method='PUT'
        )
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            ok += 1
            if ok % 20 == 0:
                print(f'  进度: {ok}/{total}')
        except Exception as e:
            err_body = e.read().decode() if hasattr(e, 'read') else '{}'
            if 'already exists' in err_body:
                ok += 1
            else:
                fail += 1
                print(f'  [FAIL] {fpath}: {str(e)[:80]}')

print(f'\n完成: {ok}/{total} 成功, {fail} 失败')
