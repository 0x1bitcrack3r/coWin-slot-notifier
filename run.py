import requests
import datetime
import urllib3
import certifi
import json
import telegram
import getopt,sys
import os

options = "s:a:"
long_options = ['slotsrange=','agelimit=']

argumentList = sys.argv[1:]
try:
    arguments, values = getopt.getopt(argumentList, options, long_options)
    for currentArgument, currentValue in arguments:
        # if currentArgument in ('-t', '--token'):
        #     TOKEN=currentValue  
        # elif currentArgument in ('-c', '--chatid'):
        #     CHAT_ID=int(currentValue)
        # elif currentArgument in ('-p', '--pincode'):
        #     PINCODE=currentValue
        if currentArgument in ('-s','--slotsrange'):
            SLOTS_FOR_NEXT_NUMBER_OF_DAYS=int(currentValue)
        elif currentArgument in ('-a','--agelimit'):
            AGE_LIMIT=int(currentValue)     
except getopt.error as err:
    print (str(err))

TOKEN = str(os.environ['TOKEN'])
if AGE_LIMIT>18:
    CHAT_ID=int(os.environ['CHAT_ID_45'])
else:
    CHAT_ID=int(os.environ['CHAT_ID_18'])
PINCODE=os.environ['PINCODE']


base_url="https://cdn-api.co-vin.in/api/v2/"
find_by_pincode=base_url+"appointment/sessions/public/calendarByPin?pincode={}&date={}"
telegram_url = "https://api.telegram.org/bot{}/sendMessage"

headers = {}
headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
headers['accept'] = 'application/json'
http = urllib3.PoolManager(ca_certs=certifi.where())

def telegram_bot_sendtext(bot_message):
    params = {'chat_id':CHAT_ID, 'text': str(bot_message)}
    response = requests.post(telegram_url.format(TOKEN), data=params)
    print (response)
    return response

base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(SLOTS_FOR_NEXT_NUMBER_OF_DAYS)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]


for INP_DATE in date_str:
    request_url=find_by_pincode.format(PINCODE, INP_DATE)
    try:
        req = http.request('GET',request_url,headers = headers)
        telegram_bot_sendtext("Test")
        content = req.data
        if (req.status==200) and ('centers' in json.loads(content.decode('utf-8'))):
            resp_json = json.loads(content.decode('utf-8'))['centers']
            if resp_json is not None:
                for slot in resp_json:
                    address=slot['address']
                    fee_type=slot['fee_type']
                    center_name=slot['name']
                    for session in slot['sessions']:
                        if session['available_capacity']>0 and AGE_LIMIT==session['min_age_limit']:
                            vaccine_date=session['date']
                            available_capacity=session['available_capacity']
                            vaccine_name=session['vaccine']
                            slots=','.join(session['slots'])
                            age_limit=session['min_age_limit']
                            message=f"Name:{center_name}\nAddress:{address}\nDate:{vaccine_date}\nCapacity:{available_capacity}\nVaccine Name:{vaccine_name}\nSlots:{slots}\nFee Type:{fee_type}\nAge Limit:{age_limit}\n\n"
                            telegram_bot_sendtext(message)
    except:
        print ("Try again")
