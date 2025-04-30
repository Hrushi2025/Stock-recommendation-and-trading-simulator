# This is a optimized version of member buy sell data where
# i have used dictonery to reduce time complexity form N^3 to N^2
# by storing symbol and id in dictonery

import random
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
    memberDict = {}

    for data in memberData:
        #print(data[0],data[1])
        memberDict[data[1]]=data[0]

    print(memberDict)

    return memberDict

def getBuySellMovingAvgData():
    cursor.execute("SELECT date_,symbol,close_,buy_signal,sell_signal FROM buy_sell_moving_avg_fact")
    buySellData = cursor.fetchall()
    buySellLst = []
    for data in buySellData:
        #if data[3] != "" or data[4] != "":
            buySellLst.append(data)

    return buySellLst


def buySellMember(memberSym, buySellData,startDate,endDate,plant):

    while startDate < endDate:
        for values in buySellData:
            if startDate in values:
                    if values[1] in memberSym and values[3] != "":
                        qty = random.randint(5,10)
                        #f.write(f"{values[0]},{memberSym[values[1]]},{values[1]},{values[3]},{values[2]},{qty},{(values[2] * qty)}\n")
                        cursor.execute("INSERT INTO member_buy_sell (date_, member_id, symbol, buy_sell, close_, qty, value, plant) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (values[0],memberSym[values[1]],values[1],values[3],values[2],qty,(values[2] * qty),plant))


                    elif values[1] in memberSym and values[4] != "":
                        qty = random.randint(1,5)
                        #f.write(f"{values[0]}, {memberSym[values[1]]}, {values[1]}, {values[4]}, {values[2]},{qty},{(- values[2] * qty)}\n")
                        cursor.execute("INSERT INTO member_buy_sell (date_, member_id, symbol, buy_sell, close_, qty, value, plant) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (values[0], memberSym[values[1]], values[1], values[4], values[2], qty, (values[2] * qty),plant))

                    # elif values[1] in memberSym:
                    #     cursor.execute("INSERT INTO member_buy_sell (date_, member_id, symbol, price, plant) VALUES(%s,%s,%s,%s,%s)",
                    #                    (values[0],memberSym[values[1]],values[1],values[2],plant))

        startDate += dt.timedelta(days=1)

    conn.commit()
    cursor.close()
    conn.close()


def main():

    maxDate = getMaxDate()
    if maxDate == None:
        startDate = dt.date(2023,1,1)
    else:
        startDate = maxDate + dt.timedelta(days=1)
    endDate = dt.date.today() + dt.timedelta(days=1)

    print(maxDate,startDate,endDate)

    memberSymbols = getMemSym()
    buySellData = getBuySellMovingAvgData()
    plant = 'python_schedular'
    buySellMember(memberSymbols,buySellData,startDate,endDate,plant)

if __name__ == "__main__":
    main()