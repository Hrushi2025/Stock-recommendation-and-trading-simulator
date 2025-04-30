from Project.configFiles import queriesConfig as qc
from dbConfig import conn

cursor = conn.cursor()

def createTableQueries():

    # Executes create table for moving average fact
    cursor.execute(qc.createTableMovingAverageFact)

    # Executes create table for rsi index fact
    cursor.execute(qc.createTableRsiIndexFact)

    # Executes create table for daily gainers and losers
    cursor.execute(qc.createTableDailyGainersLosers)

    # Executes create table for buy sell moving average
    cursor.execute(qc.createTableBuySellMovingAverage)

    # Executes create table for buy sell symbols
    cursor.execute(qc.createTableBuySellSymbols)

def truncateTableQueries():

    # Truncates data from moving average fact table
    #cursor.execute(qc.truncateTableMovingAverageFact)

    # Truncates data from rsi index fact table
    #cursor.execute(qc.truncateTableRsiIndexFact)

    # Truncates data from daily gainers and losers fact table
    cursor.execute(qc.truncateTableDailyGainersLosers)

    # Truncates data from buy sell moving average table
    #cursor.execute(qc.truncateTableBuySellMovingAverage)

    # Truncates data from buy sell symbols table
    #cursor.execute(qc.calculateBuySellSymbols)



def insertTableQueries():

    #Executes moving avg query
    cursor.execute(qc.calculateMovingAverage)
    conn.commit()


    # Executes rsi index query
    cursor.execute(qc.calculateRsiIndex)
    conn.commit()


    # Executes daily gainers and losers query
    cursor.execute(qc.calculateDailyGainersLosers)
    conn.commit()


    # Executes buy sell over moving average query
    cursor.execute(qc.calculateBuySellMovingAverage)
    conn.commit()


    # Executes buy sell symbols query
    cursor.execute(qc.expand_symbol_data_length)
    cursor.execute(qc.calculateBuySellSymbols)
    conn.commit()




def main():

    # createTableQueries()
    #
    truncateTableQueries()

    insertTableQueries()

    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()