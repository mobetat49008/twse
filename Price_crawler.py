#from IPython.display import display, clear_output
from urllib.request import urlopen
import datetime
import sched
import time as TI
import json

s = sched.scheduler(TI.time, TI.sleep)

def Repeat_Call(query_url):
    
    TI.sleep(4)
    try:
        data = json.loads(urlopen(query_url).read().decode('utf-8'))
    except:
        data = Repeat_Call(query_url)
    return data
    

def stock_price_crawler(targets):    
#    clear_output(wait=True)  
    # 組成stock_list
    stock_list = '|'.join('tse_{}.tw'.format(target) for target in targets) 
    #stock_list = stock_list + '|'.join('otc_{}.tw'.format(target) for target in targets)     
    #　query data
    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list
    try:
        data = json.loads(urlopen(query_url).read().decode('utf-8'))
    except Exception as e:   
        print('price connect error - msg:',e)    
        data = Repeat_Call(query_url) 
    # 紀錄更新時間
    time = datetime.datetime.now()  
    update_time = str(time.hour)+":"+str(time.minute)+":"+str(time.second)
   
    price = {}
    price['Update_Time'] = update_time 
    Fail_list = []
    for i in range(len(targets)):
        if 'z' in data['msgArray'][i]:
            price[targets[i]] = float(data['msgArray'][i]['z'])
        else:
            Fail_list.append(targets[i])
    '''
    start_time = datetime.datetime.strptime(str(time.date())+'9:30', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(time.date())+'13:30', '%Y-%m-%d%H:%M')

    # 判斷爬蟲終止條件
    if time >= start_time and time <= end_time:
        s.enter(1, 0, stock_crawler, argument=(targets,))
    '''
    return price, Fail_list

def stock_change_crawler(targets):    
#    clear_output(wait=True)  
    # 組成stock_list
    stock_list = '|'.join('tse_{}.tw'.format(target) for target in targets) 
    #stock_list = stock_list + '|'.join('otc_{}.tw'.format(target) for target in targets)     
    #　query data
    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list
    try:
        data = json.loads(urlopen(query_url).read().decode('utf-8'))
    except Exception as e:   
        print('change connect error - msg:',e)    
        data = Repeat_Call(query_url)

    # 紀錄更新時間
    time = datetime.datetime.now()  
    update_time = str(time.hour)+":"+str(time.minute)+":"+str(time.second)
   
    change = {}
    change['Update_Time'] = update_time 
    for i in range(len(targets)):
        if 'msgArray' not in data:
            continue
        if 'pz' in data['msgArray'][i] and 'y' in data['msgArray'][i]:
            change[targets[i]] = (float(data['msgArray'][i]['pz'])-float(data['msgArray'][i]['y']))*100/float(data['msgArray'][i]['y'])
        #else:
            #print(targets[i])
            
    '''
    start_time = datetime.datetime.strptime(str(time.date())+'9:30', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(time.date())+'13:30', '%Y-%m-%d%H:%M')

    # 判斷爬蟲終止條件
    if time >= start_time and time <= end_time:
        s.enter(1, 0, stock_crawler, argument=(targets,))
    '''
    return change



if __name__ == '__main__':        
    # 欲爬取的股票代碼
    stock_list = ['t00']

    # 每秒定時器
    #s.enter(1, 0, stock_crawler, argument=(stock_list,))
    #s.run()

    a = stock_price_crawler(stock_list)
    print(a['Update_Time'])
    for item in stock_list:
        print(a[item])