import pandas as pd
import datetime as dt
from dbConfig import conn
import yfinance as yf


cursor = conn.cursor()

pd.set_option("display.max_columns",None)


def getSymbols():

    cursor.execute("SELECT symbol FROM symbol_dimension")
    data = cursor.fetchall()

    symbols = [item[0] for item in data ]

    return symbols


def getMaxDate():

    cursor.execute("SELECT MAX(date_) from stock_daily_staging")
    date = cursor.fetchall()[0][0]

    return date


def getStockData(symbols, start_date, end_date):

        print("getting data...")
        record = []
        #symbols = symbols[0:5] # for testing first 5 stocks
        for sym in symbols:
            sdata = yf.Ticker(sym+".NS").history(start=start_date, end=end_date)
            #print(sdata)
            for date,data in sdata.iterrows():
                record.append([
                    date.strftime("%Y-%m-%d"),
                    sym,
                    data['Open'],
                    data['High'],
                    data['Low'],
                    data['Close'],
                    data['Volume'],
                    ((data['Close'] * data['Volume']) / 10 ** 7),
                    data['Dividends'],
                    data['Stock Splits']
                   ])
        return record


def dataFrames(record):

    staging_data = pd.DataFrame(record,columns=['date','symbol','open','high','low','close','volume','turnover','dividends','stock splits'])
    #print(staging_data)

    cursor.execute("SELECT symbol_id,symbol,series from symbol_dimension")
    symbol_data = cursor.fetchall()
    symbol_df = pd.DataFrame(symbol_data,columns=['symbol_id','symbol','series'])

    merged_data = pd.merge(staging_data,symbol_df,on="symbol",how='inner')

    staging = merged_data[['symbol_id','date','symbol','open','high','low','close','volume','turnover','dividends','stock splits']]

    fact = merged_data[['symbol_id','date','symbol','series','open','high','low','close']]

    return (staging,fact)


def toSql(staging,fact):

    staging.sort_values(['date','symbol'])
    fact.sort_values(['date','symbol'])

    staging.to_csv("new_file.csv")

    print(staging,"\n",fact)


    insert_staging = """INSERT INTO stock_daily_staging
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    for item,row in staging.iterrows():
        cursor.execute(insert_staging,tuple(row))
    conn.commit()

    insert_fact = """INSERT INTO stock_daily_fact
                     values(%s,%s,%s,%s,%s,%s,%s,%s)"""

    for item,row in fact.iterrows():
        cursor.execute(insert_fact,tuple(row))
    conn.commit()

    cursor.close()
    conn.close()


def main():
    symbols = getSymbols()

    start_date = getMaxDate() + dt.timedelta(days=1)
    #print(start_date,dt.date.today())

    if start_date == dt.date.today():
        print("Start date is today's date")
        start_date = dt.date.today()
        end_date = start_date + dt.timedelta(days=1)
    else:
        start_date = getMaxDate() + dt.timedelta(days=1)
        end_date = dt.date.today()

    print(start_date,end_date)
    record = getStockData(symbols, start_date, end_date)
    staging,fact = dataFrames(record)
    toSql(staging,fact)


if __name__ == "__main__":
    main()