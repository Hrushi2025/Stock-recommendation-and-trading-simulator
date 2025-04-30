from pymysql.converters import escape_date
from dbConfig import conn

if conn.is_connected():
    print("IS connected")

cursor = conn.cursor()

def fetchData():
    # Fetch data from the buy_sell_moving_avg_fact table
    cursor.execute("SELECT * FROM buy_sell_moving_avg_fact")
    data = cursor.fetchall()
    return data

def getFirstSellDates(data):
    # Dictionary to store first BUY and SELL dates for each key (e.g., stock symbol or ID)
    dataDict = {}

    # Iterating over fetched data
    for item in data:
        key = item[2]  # Assuming item[2] is a unique identifier (e.g., stock symbol or ID)

        # Check if the key exists in the dictionary
        if key not in dataDict:
            # Only consider the first occurrence if it's "BUY"
            if item[7] == "BUY":  # Assuming item[7] holds the action 'BUY' or 'SELL'
                dataDict[key] = [item[1], item[7]]  # Store the date (item[1]) and action
        else:
            # If the key exists and the next occurrence is "SELL", append it
            if item[8] == "SELL" and "SELL" not in dataDict[key]:
                dataDict[key].extend([item[1], item[8]])  # Append the date and action "SELL"

    # Remove entries where the first action is "SELL"
    filteredDataDict = {k: v for k, v in dataDict.items() if v[1] == "BUY"}

    print(filteredDataDict)
    return filteredDataDict

def main():
    data = fetchData()  # Fetch data from the database
    getFirstSellDates(data)  # Process the data to get first BUY and SELL dates

if __name__ == "__main__":
    main()
