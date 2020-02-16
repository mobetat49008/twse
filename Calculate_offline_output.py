import Price_crawler_threading as Pc
import json
import time
import sched
#import Line_test
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import goodinfo
import threading
from queue import Queue
import tkinter as tk

s = sched.scheduler(time.time, time.sleep)
token = 'kNrW93XBFwlQmDizAm1TTHrWZsTG8ZTuaWqyrN3U9s5'
#token = 'I5HvbkSz66CZ7RL3k2BkXmvMcNVLdib0J8fSPIvq3dx' #backup token
token2 = 'Vr5QUop64kp7JXpTQdAyr2dqzrnyraREB5vsg3CCxUR'

urlsplitlength = 160 #166
stock_list=None 
Weight=None 
Index = 12001.01
last_PreIndex = Index
last_PreIndex=0

window = tk.Tk()
window.title('貓貓試搓')
window.geometry('250x150')
l = tk.Label(window, text= '', font=('Arial', 12), width=30, height=30)
 

def Load_Stock_List(list_file):

    f = open(list_file , 'r' , encoding='utf8', newline='')
    Stock_List = (f.read()).split()

    return Stock_List

def Get_Price(stock_list):
    price = {}
    Fail_list = []
    for i in range(len(stock_list)//urlsplitlength +1):
        small_stock_list = stock_list[i*urlsplitlength:min(len(stock_list),(i+1)*urlsplitlength)]
        small_price, small_Fail = Pc.stock_price_crawler(small_stock_list)
        price = {**price, **small_price}
        Fail_list = Fail_list + small_Fail
    
    return price, Fail_list

def Get_change(stock_list, req_item):
    change = {}
    threads = []
    result = Queue()
    for i in range(len(stock_list)//urlsplitlength +1):
        small_stock_list = stock_list[i*urlsplitlength:min(len(stock_list),(i+1)*urlsplitlength)]
        t = threading.Thread(target=Pc.stock_change_crawler, args=(small_stock_list, req_item, result))
        t.start()
        threads.append(t)
        
    for thread in threads:
        thread.join()
    for i in range(len(stock_list)//urlsplitlength +1):
        small_change = result.get()
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
    for item in price:
        if item in shared:
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

def BOX_SHOW(msg):
    global l         
    l.config(text= msg) 
    l.pack()
    return
   
            
def process(stock_list, weight, req_item):
    global last_PreIndex
    if req_item == 'pz':
        IND = '\n試搓指數:'
    elif req_item == 'z':
        IND = '\n現貨試算指數:'
    else:
        return 'Input Error'
    
    Change = Get_change(stock_list, req_item)
    P = Calculate_percent(Change, weight)
    Premarket = Index*P/100
    PreIndex = Index + Premarket   
    msg = IND + str('%.2f'%PreIndex) + '\n漲跌點數:' + str('%.2f'%Premarket)+'\n漲跌幅:'+ str('%.3f'%P) + '% \n資料時間：' + Change['Update_Time']
    #print(msg)
    BOX_SHOW(msg)
    #window.after(500,process, stock_list, weight, req_item, twseopen)
    '''
    if abs(last_PreIndex - PreIndex)>1:        
        Line_test.lineNotifyMessage(token, msg)
        last_PreIndex = PreIndex
    else:
        Line_test.lineNotifyMessage(token2, msg)
    '''
    now_time = datetime.datetime.now()
    start_time = datetime.datetime.strptime(str(now_time.date())+'8:30', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(now_time.date())+'9:00', '%Y-%m-%d%H:%M')
    if now_time >= start_time and now_time <= end_time:
        req_item = 'pz'
    start_time = datetime.datetime.strptime(str(now_time.date())+'13:25', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(now_time.date())+'13:30', '%Y-%m-%d%H:%M')
    if now_time >= start_time and now_time <= end_time:
        req_item = 'pz'
    else:
        req_item = 'z'       

    window.after(500,process, stock_list, weight, req_item)
        
    return 'Finish'

def Show_process(stock_list, weight, req_item, twseopen):
    print('start')
    window.after(500,process, stock_list, weight, req_item, twseopen)
    
    return

def EveryDay_Update():    
    global stock_list
    print('Update Start')
    stock_list = Load_Stock_List('Stock_list.txt')
    
    stock_list.append('t00')
    Price, Fail_list = Get_Price(stock_list)

    for item in Fail_list:
        Price[item] = goodinfo.Get_PreClose(item)
        print(item, Price[item])
        
    Shared = Load_shared('shared.txt')
    Weight = Calculate_Weight(Price,Shared)
    Record_Json(Weight, 'Weight.json')
    Index_dict = {}
    Index_dict['Index'] = Price['t00']
    Index_dict['Time'] = str(datetime.datetime.now().date())
    Record_Json(Index_dict, 'Index.json')
    print('Update Finish')
    
    
def Reload_parameter():
    global stock_list, Weight, Index, last_PreIndex
    stock_list = Load_Stock_List('Stock_list.txt')
    Weight = Read_Json('Weight.json')
    Index_dict = Read_Json('Index.json')
    Index = Index_dict['Index']
    last_PreIndex = Index
    
def TWSE_Update():
    twse_close = Pc.stock_price_crawler(['t00'])
    Index_dict = {}
    Index_dict['Index'] = twse_close [0]['t00']
    Index_dict['Time'] = str(datetime.datetime.now().date())
    Record_Json(Index_dict, 'Index.json')
    
def Start_process():
    now_time = datetime.datetime.now()
    start_time = datetime.datetime.strptime(str(now_time.date())+'8:30', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(now_time.date())+'9:00', '%Y-%m-%d%H:%M')
    if now_time >= start_time and now_time <= end_time:
        req_item = 'pz'
    start_time = datetime.datetime.strptime(str(now_time.date())+'13:25', '%Y-%m-%d%H:%M')
    end_time =  datetime.datetime.strptime(str(now_time.date())+'13:30', '%Y-%m-%d%H:%M')
    if now_time >= start_time and now_time <= end_time:
        req_item = 'pz'
    else:
        req_item = 'z' 
    process(stock_list,Weight,req_item)
    return


if __name__ == '__main__': 

    Reload_parameter()   
    b = tk.Button(window, text='start', width=15, height=2, command = Start_process)
    b.pack(side='bottom') 
    scheduler = BackgroundScheduler()
    scheduler.add_job(Reload_parameter, trigger='cron', day_of_week='mon-fri', hour='08', minute="00", second="0",id='my_job_id',misfire_grace_time=30)
    scheduler.add_job(EveryDay_Update, trigger='cron', day_of_week='mon-fri', hour='21', minute="00", second="0",id='my_job_id_1',misfire_grace_time=30)
    scheduler.start()
    window.mainloop()
    

        
