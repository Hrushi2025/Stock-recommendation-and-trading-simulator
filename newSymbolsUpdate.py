## This is a important program which takes the data from 1 csv file and create table symbol staging

import datetime as dt
from Project.configFiles.dbConfig import conn

# check if database is connected or not
if conn.is_connected():
    print('Connected')

# create cursor for query execution
cursor = conn.cursor()

# truncate symbol_staging table
cursor.execute(""" TRUNCATE TABLE symbol_staging """)


# Function for update symbol data into symbol dimension table
# it take data from a csv file and insert it into symbol staging table
# then it compare data of staging and dimension and the symbols which are not in dimension table it
# inserts then into it
# source file :- EQUITY_L.csv  -- downloaded from nse site
# target file :- symbol_staging table
## -- for symbol dimension table
# source file :- symbol_staging table
# target file :- symbol_dimension table
def updateSymbols():

    with open("./EQUITY_L.csv",'r') as f:
        next(f)
        for line in f:
            SYMBOL,NAME_OF_COMPANY,SERIES,DATE_OF_LISTING,PAID_UP_VALUE,MARKET_LOT,ISIN_NUMBER,FACE_VALUE = line.strip().split(",")

            #print(SYMBOL,NAME_OF_COMPANY,SERIES,DATE_OF_LISTING,PAID_UP_VALUE,MARKET_LOT,ISIN_NUMBER,FACE_VALUE)
            cursor.execute("INSERT INTO symbol_staging VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(SYMBOL,NAME_OF_COMPANY,SERIES,dt.datetime.strptime(DATE_OF_LISTING,"%d-%b-%Y"),PAID_UP_VALUE,MARKET_LOT,ISIN_NUMBER,FACE_VALUE))
        conn.commit()

    f.close()

    cursor.execute("""
    INSERT INTO symbol_dimension_table (
        SYMBOL,
        NAME_OF_COMPANY,
        SERIES,
        DATE_OF_LISTING,
        PAID_UP_VALUE,
        MARKET_LOT,
        ISIN_NUMBER,
        FACE_VALUE
    )
    SELECT 
        SYMBOL, 
        NAME_OF_COMPANY, 
        SERIES, 
        DATE_OF_LISTING, 
        PAID_UP_VALUE, 
        MARKET_LOT, 
        ISIN_NUMBER, 
        FACE_VALUE
    FROM symbol_staging
    WHERE SYMBOL NOT IN (
        SELECT SYMBOL 
        FROM symbol_dimension_table
    );""")

    conn.commit()
    cursor.close()
    conn.close()


# main method
def main():
    updateSymbols()



if __name__ == "__main__":
    main()

