# Options-Trading-Bot-Angel-Broking-


This is a full-stack trading app based on options, developed using Django. The app allows you to host it on your own cloud server, enabling you to monitor your trades from any device throughout the day. The strategy description can be found at the end of the page.
It is mentioned that the strategy has been updated according to the new API changes in **Angel Broking**.


>This Single Dashboard can be used for all your trading bots at once, just keep adding pages for each bot, and try to have only single page for present positions and order history

![Alt text](https://github.com/sudhanshu8833/Options_Bot_Angel.git/blob/master/screenshots/login.png)


## Procedure To install this on your PC


 - Make Virtual env `virtualenv env`
 - Activate virtual enviroment `source env/bin/activate`
 - Install requirements. `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
 - complete migrations through `python3 manage.py makemigrations` and `python3 manage.py migrate`
 - Run command to start the project `python3 manage.py runserver`



```
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```




1. **Deployment**
   - Docker -> Made a docker Image for the django application, and a docker-compose file to automate some part of Deployment on live surver
   - Nginx -> Used Nginx for basic rerounting of the Requests to the PORT 80, configured to port 8080, since the **Django Docker application is hosted at port 8080**
   - Digitalocean -> Took a basic Droplet at digitalocean, Thought a kubernetes cluster would be an overkill for this project at this stage, hence this should work for now
   - Github actions -> Added the `.github/workflows/deploy.yml` file to deploy **automatically to the Digitalocean server**, Added the action button at push action (Takes a linux server and pushes to the <ip-address> with <specified> user.
     


1. **Settings page (main page)**
   ![Alt text](https://github.com/sudhanshu8833/Options_Bot_Angel.git/blob/master/screenshots/dashboard.png)
   - This should be accessible at `http://127.0.0.1:8000/start_strategy/` if you are using local host
   - Angel Api keys, client id, password and token are provided by Angel/SMARTapi Itself.
   - You will have to keep **Weekly expriy / monthly expiry** updated for it to run logically.
   - Lots -> Quatity you want to buy in one lot.
   - bots -> on/off. (If you want to keep the bot trading or not).
   - 
   - paper -> on/off (trade real money or not)
   - shift position -> If you want the bot to shift position according to losses or square off directly.


2. **current positions page**

  - available at `http://127.0.0.1:8000/option_bot/position/` if you are running on local hosts
  - The details on the table are more or less self explanatory, if any doubts, ping me anywhere.



3. **order history page**

  - available at `http://127.0.0.1:8000/option_bot/order/` on local host.
  - here also the fields are similar to positions page.






## Strategy Explanation

>Strategy is short straddle stratgy (**calender spread strategy**). Have a basic Idea of this options strategy before getting on the actual strtagy itself.


- selling at 9:20 strike price at entry time. (sell PE / CE current expiry) (recieved preimum is rounded off by 50) (lets call it **max pain**)
- Buy at same time (max pain + (recieved premium + difference)) → CE (Monthly expiry)
- Buy at same time (max pain - (recieved premium + difference)) → PE (monthly expiry)
- Exit at exit time (**3:20** in our case)/or/
- strike price reaches (Buyed CE strike + stop loss)
- strike price reaches (Buyed PE strike - stop loss)
- stoploss is set through dashboard.


