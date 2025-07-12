import os, re, urllib.request, requests, m3u8
from Crypto.Cipher import AES
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config   import headers
from crawler  import prepareCrawl
from merge    import mergeMp4
from delete   import deleteM3u8, deleteMp4
from cover    import getCover
from encode   import ffmpegEncode

# ────────────────────────────────────────────────────────────────
# encode_method：0=不轉檔 1=Remux 2=NVENC 3=CPU
# out_dir      ：輸出到哪個絕對路徑
# prompt       ：False 時完全無互動
# ────────────────────────────────────────────────────────────────
def download(url, *, encode_method: int = 0, out_dir: str = '.', prompt: bool = True):

    # 互動模式下可覆蓋 encode_method
    if prompt and encode_method == 0:
        a = input('要轉檔嗎？[y/n] ').lower()
        if a == 'y':
            a = input('[1:重封裝 2:NVENC 3:CPU] ')
            encode_method = {'1':1, '2':2, '3':3}.get(a, 1)

    print('正在下載影片:', url)

    # ── 建立番號資料夾 ───────────────────────────────────────
    dir_name   = url.rstrip('/').split('/')[-1]
    folderPath = os.path.join(out_dir, dir_name)
    os.makedirs(folderPath, exist_ok=True)

    if os.path.exists(os.path.join(folderPath, f'{dir_name}.mp4')):
        print('番號資料夾已存在，跳過…')
        return

    # ── Selenium 取得 m3u8 連結 ────────────────────────────
    chrome_opts = Options()
    chrome_opts.add_argument('--headless')
    chrome_opts.add_argument('--no-sandbox')
    chrome_opts.add_argument('--disable-dev-shm-usage')
    chrome_opts.add_argument('--disable-extensions')
    chrome_opts.add_argument('user-agent=Mozilla/5.0')

    dr = webdriver.Chrome(options=chrome_opts)
    dr.get(url)
    match = re.search(r"https://.+?\.m3u8", dr.page_source)
    if not match:
        print('❌ 找不到 m3u8，可能網頁結構改變')
        return
    m3u8url = match[0]

    # 下載 m3u8
    m3u8file = os.path.join(folderPath, f'{dir_name}.m3u8')
    urllib.request.urlretrieve(m3u8url, m3u8file)

    # 解析 m3u8，拿 key / ts 列表
    m3u8obj = m3u8.load(m3u8file)
    base_url = '/'.join(m3u8url.split('/')[:-1])

    tsList, m3u8uri, m3u8iv = [], '', ''
    for key in m3u8obj.keys or []:
        if key:
            m3u8uri, m3u8iv = key.uri, key.iv
    for seg in m3u8obj.segments:
        tsList.append(f"{base_url}/{seg.uri}")

    # 取得解密器（如有）
    if m3u8uri:
        key_bin = requests.get(f"{base_url}/{m3u8uri}", headers=headers, timeout=10).content
        iv_bin  = m3u8iv.replace("0x", "")[:16].encode()
        cipher  = AES.new(key_bin, AES.MODE_CBC, iv_bin)
    else:
        cipher = ''

    # 清 m3u8 檔
    deleteM3u8(folderPath)

    # 爬 & 下載 ts → mp4
    prepareCrawl(cipher, folderPath, tsList)
    mergeMp4(folderPath, tsList)
    deleteMp4(folderPath)

    # 下載封面
    getCover(html_file=dr.page_source, folder_path=folderPath)

    # 轉檔
    ffmpegEncode(folderPath, dir_name, encode_method)

    print('✅ 完成:', dir_name)
