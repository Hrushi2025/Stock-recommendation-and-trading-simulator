# In this program we are inserting data in cal_dim table holiday_dim and trading_dim table
# make sure you have created tables with required columns
# make sure holiday_dim is updated as you need to download csv file for each year of nse holidays and give it below for inserting values
# and update those dates in holiday_dim table
# imp:- make sure you see the truncate query below and uncomment it before you run program and make changes accordingly
# imp:- in main method you need to specify the start date and end date for creating cal_dimension and trading_dimension

import datetime as dt
import pandas as pd
from Project.configFiles.dbConfig import conn


## Test connection
if conn.is_connected():
    print('Connected')


# If there is saturday and sunday this function returns 1 means yes there is sunday and saturday
# i.e weekend
def isWeekendFind(start_date):
    return 1 if start_date.strftime('%A') in ['Saturday', 'Sunday'] else 0

# This function returns quarter respected to given months in the list
# if given_date.month is in those values then it is that quarter
def quarterFind(start_date):
    if start_date.month in [1, 2, 3, 4]:
        return 'Q1'
    elif start_date.month in [5, 6, 7, 8]:
        return 'Q2'
    else:
        return 'Q3'


# calendar is the main program that used to generate calendar and insert data
# in calendar table, holiday table and trading dimension table
# target table :- calendar_dimension
def calendar(cursor,start_date, end_date):

    #Truncating tables

    # truncate_cal_query = 'TRUNCATE TABLE calendar_dimension'
    # cursor.execute(truncate_cal_query)
    #
    # truncate_holiday_query = 'TRUNCATE TABLE holiday_dimension'
    # cursor.execute(truncate_holiday_query)
    #
    # truncate_trading_query = 'TRUNCATE TABLE trading_dimension'
    # cursor.execute(truncate_trading_query)

    # insert query for cal_dimension table
    insert_query_cal_dim = """INSERT INTO calendar_dimension(DATE_, DAY_OF_MONTH, DAY_OF_WEEK, IS_WEEKEND, 
                                                    WEEK_OF_YEAR, MONTH_, MONTH_NUMBER, QUARTER_, YEAR_)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    while start_date <= end_date:
        is_weekend = isWeekendFind(start_date)
        quarter = quarterFind(start_date)
        date_ = start_date
        day_of_month = start_date.strftime('%d')
        day_of_week = start_date.strftime('%A')
        month_ = start_date.strftime("%B")
        month_number = start_date.month
        year_ = start_date.year
        week_of_year = start_date.isocalendar()[1]

        records = (date_, day_of_month, day_of_week, is_weekend, week_of_year, month_, month_number, quarter, year_)

        cursor.execute(insert_query_cal_dim, records)

        start_date += dt.timedelta(days=1)

    conn.commit()


# here in query the data is changed according to the need of trading dimension table
# like the holidays are removed and ranking the dates partition by year and order by date
# inserting data into trading_dim_table
# source_table :- calendar_dimension table
# target table:- trading_dimension table
def tradingDimension(cursor):

    insert_query_trading_dim = """
    INSERT INTO trading_dimension (RANK_, DATE_, DAY_OF_MONTH, DAY_OF_WEEK, IS_WEEKEND, WEEK_OF_YEAR, MONTH_, MONTH_NUMBER, QUARTER_, YEAR_)
    select 
    rank() OVER(partition by year(DATE_) order by DATE_) as RANK_,
    DATE_,
    DAY_OF_MONTH,
    DAY_OF_WEEK,
    IS_WEEKEND,
    WEEK_OF_YEAR, 
    MONTH_,
    MONTH_NUMBER,
    QUARTER_,
    YEAR_
    FROM calendar_dimension cd
    WHERE cd.DATE_ NOT IN (SELECT DATE_ FROM holiday_dimension) 
    AND cd.IS_WEEKEND = 0
    """
    cursor.execute(insert_query_trading_dim)



# the holiday data is taken from nse stock website and converted to csv
# then inserting it into holiday_dimension_table
# you need to always download the holiday_csv from nse for this function
# source_table :- holiday_dimension dataframe from csv
# target_table :- holiday_dimension table
def hoildayDim(cursor,df1):

    df1['Date'] = df1['Date'].str.strip()  # Remove any extra whitespace
    df1['Date'] = pd.to_datetime(df1['Date'], format='%B %d %Y', errors='coerce').dt.strftime('%Y-%m-%d')

    insert_holiday = "INSERT INTO holiday_dimension(HOLIDAY_NAME,DATE_,DAY_) VALUES(%s, %s, %s)"

    for index, row in df1.iterrows():
                #print(row[1])
            cursor.execute(insert_holiday,tuple(row))


# main query to call the calendar function, Holiday Function
# here you need to give the dates to get calendar, and trading dimension table
def main():
    start_date = dt.date(2023, 1, 1)
    end_date = dt.date(2025, 12, 31)
    cursor = conn.cursor()

    calendar(cursor,start_date, end_date)

    df1 = pd.read_csv('./Holiday_Dim.csv')
    hoildayDim(cursor, df1)

    tradingDimension(cursor)

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
