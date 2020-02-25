import requests
#import datetime

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
	
    payload = {'message': msg}
    try:
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    except Exception as e:   
        print('Line notify error - msg:',e)
        print(msg)    
    return

'''
NOW = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')	
message = '感覺還行的小玩意：'+NOW
token = 'Vr5QUop64kp7JXpTQdAyr2dqzrnyraREB5vsg3CCxUR'
lineNotifyMessage(token, message)
#token = 'I5HvbkSz66CZ7RL3k2BkXmvMcNVLdib0J8fSPIvq3dx'
#lineNotifyMessage(token, message)
'''