# -*- coding: utf-8 -*-
"""
Created on Sun May 17 14:19:05 2020

@author: BreezeCat
"""

import xlwings as xw
import datetime

Item_Dict={'z':'F', 'y':'D', 'pz':'C', 'c':'A'}

workbook = xw.Book('ESUN.xlsx')
sheet = workbook.sheets['工作表1']

def stock_price_crawler(targets):
    data = {}
    data['msgArray'] = []
    for item in targets:
        temp = {}
        row = int(item)
        temp['z'] = sheet.cells(row, Item_Dict['z']).value
        temp['y'] = sheet.cells(row, Item_Dict['y']).value
        temp['c'] = sheet.cells(row, Item_Dict['c']).value
        data['msgArray'].append(temp)
    # 紀錄更新時間
    time = datetime.datetime.now()  
    update_time = str(time.hour)+":"+str(time.minute)+":"+str(time.second)
    price = {}
    price['Update_Time'] = update_time 
    Fail_list = []
    for i in range(len(data['msgArray'])):
        if 'z' in data['msgArray'][i]:
            if data['msgArray'][i]['z'] != '--' and data['msgArray'][i]['z'] != None:
                price[data['msgArray'][i]['c']] = float(data['msgArray'][i]['z'])
            elif data['msgArray'][i]['y'] != '--' and data['msgArray'][i]['y'] != None:
                price[data['msgArray'][i]['c']] = float(data['msgArray'][i]['y']) 
    
    return price, Fail_list

def stock_change_crawler(targets, req_item, result): 
    data = {}
    data['msgArray'] = []
    for item in targets:
        temp = {}
        row = int(item)
        temp[req_item] = sheet.cells(row, Item_Dict[req_item]).value
        temp['y'] = sheet.cells(row, Item_Dict['y']).value
        temp['c'] = sheet.cells(row, Item_Dict['c']).value
        data['msgArray'].append(temp)
    
     # 紀錄更新時間
    time = datetime.datetime.now()  
    update_time = str(time.hour)+":"+str(time.minute)+":"+str(time.second)
   
    change = {}
    change['Update_Time'] = update_time 
    for i in range(len(data['msgArray'])):
        if req_item in data['msgArray'][i] and 'y' in data['msgArray'][i]:
            if data['msgArray'][i][req_item] != None and data['msgArray'][i][req_item] != '--' and data['msgArray'][i]['y'] != None:
                change[data['msgArray'][i]['c']] = (float(data['msgArray'][i][req_item])-float(data['msgArray'][i]['y']))*100/float(data['msgArray'][i]['y'])
            
    result.put(change)
    return


if __name__ == '__main__':        
    # 欲爬取的股票代碼
    stock_list = ['2002','2330','2317','3557','2884']
    a, b = stock_price_crawler(stock_list)
    print(a)
'''
for i in range(2,944):
    num = sheet.cells(i,1).value
    row = int(num)
    sheet.cells(row,1).value = "=XQESUNAP|Quote!'"+num+".TW-ID'"
    sheet.cells(row,2).value = "=XQESUNAP|Quote!'"+num+".TW-Name'"
    sheet.cells(row,3).value = "=XQESUNAP|Quote!'"+num+".TW-SimulatePrice'"
    sheet.cells(row,4).value = "=XQESUNAP|Quote!'"+num+".TW-PreClose'"
    sheet.cells(row,5).value = "=XQESUNAP|Quote!'"+num+".TW-SimulateTime'"
    sheet.cells(row,6).value = "=XQESUNAP|Quote!'"+num+".TW-Price'"
'''