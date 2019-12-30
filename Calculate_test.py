import Price_crawler as Pc
import json
import time
import sched
import Line_test
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
#import MarketValue_from_FinMind as MV
s = sched.scheduler(time.time, time.sleep)
token = 'I5HvbkSz66CZ7RL3k2BkXmvMcNVLdib0J8fSPIvq3dx'
token2 = 'Vr5QUop64kp7JXpTQdAyr2dqzrnyraREB5vsg3CCxUR'


urlsplitlength = 166
stock_list=None 
Weight=None 
Index = 12001.01
last_PreIndex = Index
last_PreIndex=0

def Load_Stock_List(list_file):

    f = open(list_file , 'r' , encoding='utf8', newline='')
    Stock_List = (f.read()).split()

    return Stock_List

def Get_Price(stock_list):
    price = {}
    
    for i in range(len(stock_list)//urlsplitlength +1):
        small_stock_list = stock_list[i*urlsplitlength:min(len(stock_list),(i+1)*urlsplitlength)]
        small_price = Pc.stock_price_crawler(small_stock_list)
        price = {**price, **small_price}
    
    return price

def Get_change(stock_list):
    change = {}
    
    for i in range(len(stock_list)//urlsplitlength +1):
        small_stock_list = stock_list[i*urlsplitlength:min(len(stock_list),(i+1)*urlsplitlength)]
        small_change = Pc.stock_change_crawler(small_stock_list)
        change = {**change, **small_change}

    return change

def Load_shared(shared_file):
    file = open(shared_file,'r',encoding = 'utf-8-sig')
    shared = {}
    line = file.readline()
    while(line):
        line = line.split(',')
        shared[line[0]] = float(line[1])
        line = file.readline()
    file.close()
    return shared

def Calculate_Weight(price, shared):
    market_value = {}
    total_market_value = 0
    for item in shared:
        market_value[item] = price[item] * shared[item]
        total_market_value = total_market_value + market_value[item]
    weight = {}
    for item in market_value:
        weight[item] = market_value[item]*100/total_market_value
    return weight
    
def Record_Json(Dict, save_name):
    file = open(save_name,'w')
    json.dump(Dict,file)
    file.close()
    return

def Read_Json(file_name):
    with open(file_name,"r", encoding='utf-8') as file:
        data = json.load(file)
        return data

def Calculate_percent(change, weight):
    percent = 0
    for item in change:
        if item in weight:
            percent = percent + change[item]*weight[item]/100
    return percent
            
def process(stock_list, weight,twseopen):
    global last_PreIndex
    Change = Get_change(stock_list)
    P = Calculate_percent(Change, weight)
    Premarket = Index*P/100
    PreIndex = Index + Premarket
    
    if abs(last_PreIndex - PreIndex)>1:
        msg = '\n[Dylan]試搓指數:'+ str('%.2f'%PreIndex) + '\n漲跌點數:' + str('%.2f'%Premarket)+'\n漲跌幅:'+ str('%.3f'%P) + '% \n資料時間：' + Change['Update_Time']
        Line_test.lineNotifyMessage(token, msg)
        last_PreIndex = PreIndex
    else:
        msg = '\n[Dylan]試搓指數:'+ str('%.2f'%PreIndex) + '\n漲跌點數:' + str('%.2f'%Premarket)+'\n漲跌幅:'+ str('%.3f'%P) + '% \n資料時間：' + Change['Update_Time']
        Line_test.lineNotifyMessage(token2, msg)
    
    
    now_time = datetime.datetime.now()
    if twseopen == True: 
        start_time = datetime.datetime.strptime(str(now_time.date())+'8:30', '%Y-%m-%d%H:%M')
        end_time =  datetime.datetime.strptime(str(now_time.date())+'9:00', '%Y-%m-%d%H:%M')
    else:
        start_time = datetime.datetime.strptime(str(now_time.date())+'13:25', '%Y-%m-%d%H:%M')
        end_time =  datetime.datetime.strptime(str(now_time.date())+'13:30', '%Y-%m-%d%H:%M')
        
    if now_time >= start_time and now_time <= end_time:
        s.enter(1, 0, process, argument=(stock_list,weight,twseopen))
        
    return 'Finish'

def EveryDay_Update(stock_list):
    
    stock_list.append('t00')
    Price = Get_Price(stock_list)
    '''
    To do:
        沒撈到的股票要重撈昨日收盤價
    '''
    Shared = Load_shared('shared.txt')
    Weight = Calculate_Weight(Price,Shared)
    Record_Json(Weight, 'Weight.json')
    Index_dict = {}
    Index_dict['Index'] = Price['t00']
    Index_dict['Time'] = str(datetime.datetime.now().date())
    Record_Json(Index_dict, 'Index.json')
    
def Reload_parameter():
    global stock_list, Weight, Index, last_PreIndex
    stock_list = Load_Stock_List('Stock_list.txt')
    Weight = Read_Json('Weight.json')
    Index_dict = Read_Json('Index.json')
    Index = Index_dict['Index']
    last_PreIndex = Index


if __name__ == '__main__': 
    stock_list = Load_Stock_List('Stock_list.txt')
    
    #stock_list.append('t00')
    #Price = Get_Price(stock_list)
    #Shared = Load_shared('shared.txt')
    '''
    Weight = Calculate_Weight(Price,Shared)
    Record_Json(Weight, 'Weight.json')
    Index_dict = {}
    Index_dict['Index'] = Price['t00']
    Index_dict['Time'] = str(datetime.datetime.now().date())
    Record_Json(Index_dict, 'Index.json')
    '''

    #Weight = Read_Json('Weight.json')
    #Index_dict = Read_Json('Index.json')
    #Index = Index_dict['Index']
    #print(Index)

    #s.enter(1, 0, process, argument=(stock_list,Weight))
    #s.run()
    
    scheduler = BackgroundScheduler()  
    scheduler.add_job(Reload_parameter, trigger='cron', day_of_week='mon-fri', hour='08', minute="00", second="0",id='my_job_id',misfire_grace_time=30)
    scheduler.start()

    scheduler = BackgroundScheduler()  
    scheduler.add_job(process, args=(stock_list,Weight,0), trigger='cron', day_of_week='mon-fri', hour='08', minute="30", second="0",id='my_job_id',misfire_grace_time=30)
    scheduler.start()
    
    scheduler1 = BackgroundScheduler()  
    scheduler1.add_job(process, args=(stock_list,Weight,1), trigger='cron', day_of_week='mon-fri', hour='13', minute="25", second="0",id='my_job_id_1',misfire_grace_time=30)
    scheduler1.start()
    
    while(1):
        #毫無意義#
        i = 0 

        