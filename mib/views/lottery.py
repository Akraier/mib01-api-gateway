from flask import Blueprint, render_template, request, abort
from flask_login import (login_user, login_required, current_user)
from werkzeug.utils import redirect 
from mib.rao.lottery_manager import LotteryManager
from datetime import date, datetime, timedelta

import json


lottery = Blueprint('lottery', __name__)

"""
Every user can guess just 1 number a month.  
Lottery extract randomly 1 number from 1 to 99, if your guess is lucky you won half of the point needed to withdrow a message of your choice.
"""
# This is useful for the user to know what number he choosed or to know if he had not already choose a number
@lottery.route('/lottery',methods = ['GET'])
@login_required
def lucky_number():
    lottery_infos = LotteryManager.retrieve_by_id(current_user.id)
    if lottery_infos is None: #no row for the user (error!)
        return render_template('lottery_board.html', action = 'Some error occurred')
    
    if lottery_infos['ticket_number'] != -1:
        return render_template('lottery_board.html',action = "You already select the number. This is your number: "+ str(lottery_infos['ticket_number'])+"!") 
    else:
        return render_template('lottery_board.html',action = "You have selected no number yet, hurry up! Luck is not waiting for you!")
    

# This route is necessary to allow user to select a number for the next lottery extraction.
# There is a time limit to choose the number: user can choose number in the first half of the month (from 1st to 15th)
@lottery.route('/lottery/<number_>',methods = ['POST'])
@login_required
def play(number_):
    
    print("HELLOOOOOOOOOOO")
    #guess a number for lottery
    last_day = 15 #last day of the month useful to select a number
    number = int(number_)
    if number in range(1,100):
        #now we check for the day of month (user can choose only in the first half of month)
        today = date.today()
        day_of_month = today.day
        if day_of_month <= last_day:
            usr_lottery_row = LotteryManager.retrieve_by_id(current_user.id)
            
            print("_____--> the rowwwww first::::::", usr_lottery_row)
            
            if usr_lottery_row['ticket_number'] == -1: #user doesn't already choose a number, so now he can. We save in the DB the number selected
                print("questa è la ROWWWWW _____ ", usr_lottery_row)
                LotteryManager.update_lottery_number(current_user.id,number)
                #return render_template('lottery_board.html',action = "You select the number "+str(number)+"! Good Luck!")
                return redirect('/lottery')
            else:
                #already choosed a number
                return redirect('/lottery')
                #return render_template('lottery_board.html',action = "You already select the number "+ str(usr_lottery_row['ticket_number'])+"! Good Luck!")
        else:
            #can't choose a number because it's expired the usefuk time (useful time: from 1st to 15th of month)
            return render_template('lottery_board.html', action = "You cannot choose any more a number, the time to partecipate to lottery is expired! Try next month!")
    else:
        return render_template('lottery_board.html', action = "You choose an invalid number for the lottery! You can choose only number from 1 to 99 !")
   