import requests
import urllib
url1 = 'https://baike.baidu.com/item/'
key_word = (input())
lens = len(key_word)
key_word = urllib.parse.quote(key_word,encoding = 'utf-8', errors = 'replace')
headers = {
    # 'wd':key_word,
    # 'Host': 'https://baike.baidu.com/item/',
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}
html = requests.get(url1+key_word,headers = headers)
print(url1+key_word)# 验证链接是否正确
html.encoding = html.apparent_encoding
print(html.text)
