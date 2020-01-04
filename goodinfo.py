# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36' }

def Get_PreClose(stock_id):
    url = 'https://goodinfo.tw/StockInfo/BasicInfo.asp?STOCK_ID=' + stock_id
    list_req = requests.post(url, headers = headers)
    soup = BeautifulSoup(list_req.content, "html.parser")
    table_tags = soup.find_all('table', limit=11)
    tr_tags = table_tags[10].find_all('tr', limit=5)
    td_tags = tr_tags[4].find_all('td', limit=5)
    #PreClose = float(td_tags[4].string) #need Check
    PreClose = float(td_tags[0].string)
    return PreClose

if __name__ == '__main__':
    C = Get_PreClose('9926')