# author: hcjohn463 (mod by Josh)
#!/usr/bin/env python
# coding: utf-8

from args import *
from download import download
from movies import movieLinks

parser = get_parser()
args   = parser.parse_args()

def _dl(target_url: str):
    download(
        url            = target_url,
        encode_method  = int(args.encode),
        out_dir        = args.output,
        prompt         = (not args.no_prompt)
    )

if args.url:
    _dl(args.url)

elif args.random:
    _dl(av_recommand())

elif args.all_urls:
    for u in movieLinks(args.all_urls):
        _dl(u)

else:
    _dl(input("輸入 Jable 網址: "))
