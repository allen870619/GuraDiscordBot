import requests
from opencc import OpenCC

# 心靈毒雞湯
# src: https://collect.xmwxxc.com/index/doc/sign/djt.html
def getPoisonSoup(mode=0):
    headers = {'user-agent': 'Mozilla/5.0'}
    url = "https://collect.xmwxxc.com/collect/djt/?type=%d"%(mode)
    soup = requests.get(url, headers=headers)
    context = soup.json()["data"]["message"]
    
    # convert simplified to traditional
    cc = OpenCC('s2t')
    return cc.convert(context)
    