import pandas as pd
import time
import traceback
from datetime import datetime
import logging
import json
import requests
import certifi
import pyotp
import pytz
from SmartApi import SmartConnect
from datamanagement.models import *
import os


#CONFIGURATIONS
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger('dev_log')
error = logging.getLogger('error_log')

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
data={}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(BASE_DIR)
file_path = os.path.join(BASE_DIR, 'background.json')
with open(file_path) as json_file:
    data=json.load(json_file)


client = MongoClient(data['mongo_uri'], server_api=ServerApi('1'),connect=False,tlsCAFile=certifi.where())
database=client[data['database']]
admin=database['admin']
position=database['position']
current_candles=database['candles']

'''
# ADMIN

{
    "username":"",
    "api_key":"",
    "client_id":"",
    "pin":"",
    "token":"",
    "lots":,
    "time_in":"9:20",
    "time_end":"",
    "addition":"200",
    "symbol":"",
    "time_end":"",
    "status":True | False,
    "live": True | False,
    "stoploss":"",
    "takeprofit":""
}

# POSITION
{
    "symbol":"",
    "status": OPEN | CLOSED,
    "type": LONG | SHORT,
    "time_start":"",
    "time_end":"",
    "quantity":"",
    "pnl":"",
    "current_price":"",
    "price_in":"",
    "price_out":"",
    "stoploss":"",
    "take_profit":""
}
'''

class run_strategy():

    count=0
    def __init__(self):
        self.ltp_prices={}
        self.times=time.time()
        
        self.admin=admin.find_one()
        self.login()
        self.debug=True
        self.positions={}
        run_strategy.count+=1


    def login(self):
        self.obj=SmartConnect(api_key=self.admin["angel_api_keys"])
        data = self.obj.generateSession(self.admin['angel_client_id'],self.admin['angel_pin'],pyotp.TOTP(self.admin['angel_token']).now())
        # refreshToken= data['data']['refreshToken']

    def this_scripts(self):

        url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data=requests.get(url=url)
        data=data.json()
        df = pd.DataFrame(data)
        results={}
        for i in range(len(df)):
            if 'NIFTY' in df['symbol'][i]:
                results[df['symbol'][i]]=df['token'][i]
            else:
                continue
        return results

    def get_ltp(self,symbol,type):
        return self.obj.ltpData(
                            type, symbol, self.tokens[symbol])['data']['ltp']

    def is_position(self,instrument):
        positions=list(position.find())

        for pos in positions:
            if(pos['status']=='OPEN'):
                return True
        return False




    def add_positions(self,instrument,type):
        pos={
            "symbol":instrument,
            "token":self.tokens[instrument],
            "status":"OPEN",
            "type":type,
            "time_start":datetime.now(tz=pytz.timezone(data['timezone'])),
            "time_end":datetime.now(tz=pytz.timezone(data['timezone'])),
            "quantity":self.admin['lots'],
            "current_price":self.get_ltp(instrument,"NFO"),
            "price_in":self.get_ltp(instrument,"NFO"),
            "price_out":0,
            "stoploss":0,
            "take_profit":0,
            "pnl":0
        }
        position.insert_one(pos)

        if(self.admin['live']):
            self.create_order(pos,"OPEN")



    def start_logic(self):
        current_index_price=self.get_ltp(self.admin['symbol'],"NSE")
        current_spot=0
        if(self.admin['symbol'].upper()=="BANKNIFTY"):
            current_spot=int(round(current_index_price/100, 0) * 100)
        else:
            current_spot=int(round(current_index_price/50, 0) * 50)

        sell_pe_symbol=self.admin['weekly_expiry']+str(current_spot)+'PE'
        sell_ce_symbol=self.admin['weekly_expiry']+str(current_spot)+'CE'
        recieved_premium_pe=self.get_ltp(sell_pe_symbol,"NFO")
        recieved_premium_ce=self.get_ltp(sell_ce_symbol,"NFO")

        hedge_difference=int(round((recieved_premium_pe+recieved_premium_ce)/100,0)*100)+self.admin['addition']
        buy_pe_symbol=self.admin['monthly_expiry']+str(current_spot-hedge_difference)+"PE"        
        buy_ce_symbol=self.admin['monthly_expiry']+str(current_spot+hedge_difference)+"CE"        

        open_positions_for=[buy_ce_symbol,buy_pe_symbol,sell_ce_symbol,sell_pe_symbol]
        order_type=["LONG","LONG","SHORT","SHORT"]

        for i in range(4):
            self.add_positions(open_positions_for[i],order_type[i])



    def create_order(self,params,type):

        try:
            pass
            # create LIVE ORDERS

        except Exception:
            error.info(str(traceback.format_exc()))

    def end_logic(self):
        positions=position.find()
        for pos in positions:
            if pos['status']=="OPEN":
                pos['status']="CLOSED"
                pos['time_end']=datetime.now(tz=pytz.timezone(data['timezone']))
                pos['price_out']=pos['current_price']
                position.update_one({"_id":pos['_id']},{"$set":pos})
                if(self.admin['live']):
                    self.create_order(pos,"CLOSE")


    def signals(self,instrument,df):
        if(not self.is_position(instrument)):
            time_now=datetime.now(tz=pytz.timezone(data['timezone']))
            time_start=self.admin['time_in'].split(":")
            if(time_now.hour==int(time_start[0]) and time_now.minute==int(time_start[1]) or self.debug):
                return "buy"
        else:
            time_now=datetime.now(tz=pytz.timezone(data['timezone']))
            time_start=self.admin['time_end'].split(":")
            if(time_now.hour==int(time_start[0]) and time_now.minute==int(time_start[1])):
                return "sell"

        return "NA"

    def close_signal(self):
        positions=position.find()
        total_pnl=0
        for pos in positions:
            if(pos['status']=="OPEN"):
                pos['current_price']=self.get_ltp(pos['symbol'],"NFO")
                if(pos['type']=='LONG'):
                    pos['pnl']=round(pos['current_price']-pos['price_in'],2)

                elif(pos['type']=='SHORT'):
                    pos['pnl']=round(pos['price_in']-pos['current_price'],2)

                total_pnl+=pos['pnl']

        if(self.admin['symbol']=="NIFTY"):
            total_pnl=total_pnl*data['nifty_lotsize']*self.admin['lots']
        else:
            total_pnl=total_pnl*data['banknifty_lotsize']*self.admin['lots']

        if(total_pnl>=self.admin['takeprofit'] or total_pnl>=-1*self.admin['stoploss']):
            self.end_logic()


    def update_current_price(self):
        positions=position.find()
        for pos in positions:
            if pos['status']=="OPEN":
                pos['current_price']=self.obj.ltpData(
                        "NFO", pos['symbol'], str(pos['token']))['data']['ltp']
                position.update_one({"_id":pos['_id']},{"$set":pos})


    def main(self):
        self.update_current_price()
        signal=self.signals()

        if(signal=="buy"):
            self.start_logic()

        elif(signal=="sell"):
            self.end_logic()

        logger.info("SIGNAL IS BEING CHECKED")
        if(self.admin['check_tpsl']):
            self.close_signal()


    def run(self):
        try:
            self.tokens=self.this_scripts()
            while True:
                if(self.admin['status']):
                    self.main()
                else:
                    time.sleep(60)

        except Exception:
            error.info(str(traceback.format_exc()))
            return str(traceback.format_exc())
