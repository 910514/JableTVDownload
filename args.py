import argparse
from bs4 import BeautifulSoup
import random
from urllib.request import Request, urlopen
from config import headers
import re
import os


def get_parser():
    parser = argparse.ArgumentParser(description="Jable TV Downloader")
    parser.add_argument("--random", type=bool, default=False,
                        help="Enter True for download random ")
    parser.add_argument("--url", type=str, default="",
                        help="Jable TV URL to download")
    parser.add_argument("--all-urls", type=str, default="",
                        help="Jable URL contains multiple avs")
        # 🔽 新增的參數
    parser.add_argument("--encode", type=int, choices=[0, 1, 2, 3], default=0,
                        help="Transcode method: 0=No, 1=Remux, 2=NVENC, 3=CPU")
    parser.add_argument("--output", type=str, default=os.getcwd(),
                        help="Download output path (absolute path)")
    parser.add_argument("--no-prompt", action="store_true",
                        help="Disable all interactive prompts")
    return parser


def av_recommand():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://jable.tv/'
    request = Request(url, headers=headers)
    web_content = urlopen(request).read()
    # 得到繞過轉址後的 html
    soup = BeautifulSoup(web_content, 'html.parser')
    h6_tags = soup.find_all('h6', class_='title')
    av_list = re.findall(r'https[^"]+', str(h6_tags))
    return random.choice(av_list)


# print(av_recommand())
