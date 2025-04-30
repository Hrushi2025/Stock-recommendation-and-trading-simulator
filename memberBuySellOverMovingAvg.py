# here we do buy sell of member over moving average the time complexity is N^3
# coplexity is reduced in optimized version

import random
from turtledemo.penrose import start

from sqlalchemy import Nullable

from dbConfig import conn
import datetime as dt

cursor = conn.cursor()


def getMaxDate():
    cursor.execute("SELECT MAX(date_) FROM member_buy_sell")
    maxDate = cursor.fetchall()[0][0]

    return maxDate


def getMemSym():
    cursor.execute("SELECT * FROM member_symbol_assignment")
    memberData = cursor.fetchall()

    return memberData


def getBuySellMovingAvgData():
    cursor.execute("SELECT date_,symbol,close_,buy_signal,sell_signal FROM buy_sell_moving_avg_fact")
    buySellData = cursor.fetchall()
    buySellLst = []
    for data in buySellData:
        if data[3] != "" or data[4] != "":
            buySellLst.append(data)

    return buySellLst



def buySellMember(memberSym, buySellData,startDate,endDate):

    while startDate < endDate:
        for values in buySellData:
            if startDate in values:
                for mem in memberSym:
                   if mem[1] == values[1] and values[3] != "":
                        qty = random.randint(5,10)
                        cursor.execute("INSERT INTO member_buy_sell VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (values[0],mem[0],values[1],values[3],values[2],qty,(values[2] * qty)))


                   elif mem[1] == values[1] and values[4] != "":
                        qty = random.randint(1,5)
                        cursor.execute("INSERT INTO member_buy_sell VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                       (values[0], mem[0], values[1], values[4], values[2], qty, (- values[2] * qty)))

        startDate += dt.timedelta(days=1)

    conn.commit()
    cursor.close()
    conn.close()



def main():


    maxDate = getMaxDate()
    startDate = None
    endDate = None

    if maxDate is not None:
        startDate = maxDate + dt.timedelta(days=1)
        endDate = dt.date.today() + dt.timedelta(days=1)
    else:
        startDate = dt.date(2023,1,1)



    print(maxDate,startDate,endDate)

    #memberSymbols = getMemSym()
    #buySellData = getBuySellMovingAvgData()
    #buySellMember(memberSymbols,buySellData,startDate,endDate)

if __name__ == "__main__":
    main()