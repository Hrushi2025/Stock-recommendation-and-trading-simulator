from dbConfig import conn

if conn.is_connected():
    print("IS connected")

cursor = conn.cursor()

def fetchData():
    cursor.execute("SELECT * FROM buy_sell_moving_avg_fact")
    data = cursor.fetchall()
    return data

def getFirstSellDates(data):
    dataDict = {}

    for item in data:
        key = item[2]

        if key not in dataDict:
            if item[7] == "BUY":
                dataDict[key] = [item[1], item[7]]
            elif item[8] == "SELL":
                dataDict[key] = [item[1], item[8]]
        else:
            if item[7] == "BUY" and "BUY" not in dataDict[key]:
                dataDict[key].append([item[1], item[7]])
            elif item[8] == "SELL" and "SELL" not in dataDict[key]:
                dataDict[key].append([item[1], item[8]])

    #print(dataDict)

    filtered_dict = {k: v for k,v in dataDict.items() if v[1] == "SELL"}
    #print(filtered_dict)
    print(len(filtered_dict))

    for key,value in filtered_dict.items():
        sym,date_,sell = key,value[0],value[1]
        print(sym,date_,sell)
        cursor.execute("DELETE FROM buy_sell_moving_avg_fact WHERE symbol = %s  and date_ = %s and sell_signal = %s",(sym,date_,sell))
        conn.commit()
    cursor.close()
    conn.close()

    return dataDict

def main():
    data = fetchData()
    getFirstSellDates(data)

if __name__ == "__main__":
    main()
