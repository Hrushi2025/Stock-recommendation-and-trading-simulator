
# Creating fact table of moving averages over 7,14,21,28 days moving averages
createTableMovingAverageFact = """

CREATE TABLE IF NOT EXISTS moving_average_fact(
rank_ INT,
date_ DATE,
symbol VARCHAR(25),
close_ DOUBLE,
avg_7_days DOUBLE,
avg_14_days DOUBLE,
avg_21_days DOUBLE,
avg_28_days DOUBLE
);
"""

# Truncate data from moving average fact table
truncateTableMovingAverageFact = """
TRUNCATE TABLE moving_average_fact;
"""



# This is the query that calculates the moving averages of 7, 14, 21, 28 days
# Source table :- stock_daily_fact table
# target table :- moving_average_fact table
calculateMovingAverage = f"""
                insert into moving_average_fact
                with cte as(
                select max(ds.date_) as max_dt 
                from stock_daily_fact ds
                ),
                cte2 as (
                SELECT td.rank_ ,ds.DATE_, SYMBOL, CLOSE_,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS moving_avg_14,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS moving_avg_21,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) AS moving_avg_28
                            from stock_daily_fact ds
                            join trading_dimension td on ds.date_ = td.date_ 
                            where ds.date_ between (select date_sub(cte.max_dt, interval 60 day) from cte) and (SELECT max_dt FROM cte)
                )
                select * from cte2
                where date_ > (select max(date_) from moving_average_fact)
            """

showMovingAverage = """SELECT * FROM moving_average_fact;"""

# Creating rsi_index fact table for calculating rsi index
createTableRsiIndexFact = """
CREATE TABLE IF NOT EXISTS rsi_index_fact(
rank_ INT,
date_ DATE,
symbol VARCHAR(20),
close_ DOUBLE,
last_date_price DOUBLE,
curr_date_price DOUBLE,
changed DOUBLE,
loss DOUBLE,
gain DOUBLE,
avg_gain_7 DOUBLE,
avg_loss_7 DOUBLE,
avg_gain_14 DOUBLE,
avg_loss_14 DOUBLE,
avg_gain_21 DOUBLE,
avg_loss_21 DOUBLE,
avg_gain_28 DOUBLE,
avg_loss_28 DOUBLE,
rs_7 DOUBLE,
rs_14 DOUBLE,
rs_21 DOUBLE,
rs_28 DOUBLE,
rsi_7 DOUBLE,
rsi_14 DOUBLE,
rsi_21 DOUBLE,
rsi_28 DOUBLE
);
"""

# Truncate data from rsi_index_fact table
truncateTableRsiIndexFact = """
TRUNCATE TABLE rsi_index_fact;
"""

# This query calculated the rsi index over 7, 14, 21, 28 days
# source table :- stock_daily_fact
# target table :- rsi_index_fact
calculateRsiIndex = f"""
                INSERT INTO rsi_index_fact
                 with cte0 as(
                                select max(ds.date_) as max_dt 
                                from stock_daily_fact ds
                ),
                cte AS (
                    SELECT 
                        td.Rank_,
                        ds.DATE_, 
                        ds.SYMBOL, 
                        ds.CLOSE_, 
                        ds.CLOSE_ AS last_date_price, 
                        LEAD(ds.CLOSE_, 1) OVER (PARTITION BY ds.SYMBOL ORDER BY ds.DATE_) AS curr_date_price
                    FROM 
                        moving_average_fact ds
                        JOIN trading_dimension td ON td.DATE_ = ds.DATE_
                        where ds.date_ between (select date_sub(cte0.max_dt, interval 60 day) from cte0) and (select max_dt from cte0)
                ),
                cte2 AS (
                    SELECT 
                        *, 
                        (curr_date_price - last_date_price) AS changed,
                        CASE 
                            WHEN curr_date_price - last_date_price < 0 
                            THEN ABS(curr_date_price - last_date_price)  
                            ELSE 0 
                        END AS Loss,
                        CASE 
                            WHEN curr_date_price - last_date_price > 0 
                            THEN curr_date_price - last_date_price 
                            ELSE 0 
                        END AS Gain
                    FROM 
                        cte
                ),
                cte3 AS (
                    SELECT 
                        *,
                        AVG(Gain) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS Avg_Gain_7,
                        AVG(Loss) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS Avg_Loss_7,
                        AVG(Gain) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS Avg_Gain_14,
                        AVG(Loss) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS Avg_Loss_14,
                        AVG(Gain) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS Avg_Gain_21,
                        AVG(Loss) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS Avg_Loss_21,
                        AVG(Gain) OVER (partition by SYMBOL order by DATE_ rows between 27 preceding and current row) as Avg_Gain_28,
                        AVG(Loss) over (partition by SYMBOL order by DATE_ rows between 27 preceding and current row) as Avg_Loss_28
                    FROM 
                        cte2
                ),
                cte4 AS (
                    SELECT 
                        *,
                        COALESCE((Avg_Gain_7 / NULLIF(Avg_Loss_7, 0)), 0) AS rs_7,
                        COALESCE((Avg_Gain_14 / NULLIF(Avg_Loss_14, 0)), 0) AS rs_14,
                        COALESCE((Avg_Gain_21 / NULLIF(Avg_Loss_21, 0)), 0) AS rs_21,
                        coalesce ((Avg_Gain_28 / nullif(Avg_Loss_28, 0)), 0) as rs_28
                    FROM 
                        cte3
                )
                SELECT 
                    *,
                    COALESCE(100 - (100 / (1 + rs_7)), 0) AS rsi_7,
                    COALESCE(100 - (100 / (1 + rs_14)), 0) AS rsi_14,
                    COALESCE(100 - (100 / (1 + rs_21)), 0) AS rsi_21,
                    coalesce(100 - (100 / (1 + rs_28)), 0) as rsi_28
                FROM 
                    cte4
                    where date_ > (select max(date_) from rsi_index_fact )
            """

showRsiIndexFact = """SELECT * FROM rsi_index_fact;"""

# Create table to calculate daily gainers and losers
createTableDailyGainersLosers = """

CREATE TABLE IF NOT EXISTS gainers_losers(
symbol_id INT,
date_ DATE,
symbol VARCHAR(50),
series CHAR(2),
result_ DOUBLE,
rankers INT
);

"""

# Truncate data from gainers and losers table
truncateTableDailyGainersLosers = """
TRUNCATE TABLE gainers_losers;
"""

# This query calculates the daily gainers and losers using close prices of last day and today
# Source table :- stock_daily_fact
# Target table :- gainers_losers
calculateDailyGainersLosers = """
                        insert into gainers_losers
                        select SYMBOL_ID, DATE_, SYMBOL, SERIES, result_, rankers from 
                        (
                        select * from (
                        SELECT SYMBOL_ID, DATE_, SYMBOL,SERIES,result_,
                                case 
                                    when result_ > 0 then RANK() OVER(order by result_ DESC) 
                                    when result_ <= 0 then RANK() over(order by result_  asc ) 
                                end as rankers,
                               RANK() OVER (ORDER BY result_) AS rank_losers,
                               RANK() OVER(order by result_ DESC) as rank_gainers
                        FROM (
                            SELECT *, 
                                   COALESCE(((today_price - last_price) / nullif(last_price,0)) * 100, 0) AS result_
                            FROM (
                                SELECT *, 
                                       LAG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_) AS last_price,
                                       CLOSE_ AS today_price
                                FROM stock_daily_fact
                            ) AS sub
                        ) AS sub2
                        where DATE_ = current_date() 
                        ) as sub3 
                        where rank_gainers between 1 and 5 or rank_losers between 1 and 5
                        ) as sub4
                        order by result_ DESC,rankers   
    
    """

showDailyGainersLosers = """SELECT * FROM gainers_losers;"""

# Creating the buy_sell_moving_avg_fact table for getting buy sell alarm over moving average
createTableBuySellMovingAverage = """
CREATE TABLE IF NOT EXISTS buy_sell_moving_avg_fact(
rank_ INT,
date_ DATE,
symbol VARCHAR(25),
close_ DOUBLE,
avg_7_days DOUBLE,
avg_14_days DOUBLE,
ress DOUBLE,
lag_7_days DOUBLE,
buy_signal VARCHAR(3),
sell_signal VARCHAR(4)
);
"""

# Truncating data from buy_sell_moving_avg_fact
truncateTableBuySellMovingAverage = """
TRUNCATE TABLE buy_sell_moving_avg_fact;
"""

# Query that calculates buy or sell alarm using moving average
# Source tables :- stock_daily_fact , moving_average_fact
# Target tables :- buy_sell_moving_average_fact
calculateBuySellMovingAverage = """
                    INSERT INTO BUY_SELL_MOVING_AVG_FACT
					WITH CTE AS(
                                    SELECT MAX(DS.DATE_) AS MAX_DT 
                                    FROM stock_daily_fact DS
                                    ),
                    CTE2 AS (
                    SELECT RANK_, DATE_, SYMBOL, CLOSE_, AVG_7_DAYS,AVG_14_DAYS, 
                    RES.result_,
                    CASE 
                        WHEN RES.result_ > 100 AND LAG(RES.result_) OVER(PARTITION BY SYMBOL ORDER BY DATE_) < 100  AND RES.result_ > LAG(RES.result_) OVER(PARTITION BY SYMBOL ORDER BY DATE_) THEN "BUY" ELSE ""
                    END AS BUY_SIGNAL,
                    CASE 
                        WHEN RES.result_ < 100 AND LAG(RES.result_) OVER(PARTITION BY SYMBOL ORDER BY DATE_) > 100 AND RES.result_ < LAG(RES.result_) OVER(PARTITION BY SYMBOL ORDER BY DATE_) THEN "SELL" ELSE ""
                    END AS SELL_SIGNAL
                    FROM 
                    (SELECT *,
                    (AVG_7_DAYS / AVG_14_DAYS) * 100 AS result_ 
                    FROM MOVING_AVERAGE_FACT MF) AS RES
                    WHERE DATE_ BETWEEN (SELECT DATE_SUB(CTE.MAX_DT, INTERVAL 60 DAY) FROM CTE) AND (SELECT MAX_DT FROM CTE)
                    )
                    SELECT * FROM CTE2
                    WHERE DATE_ > (SELECT MAX(DATE_) FROM BUY_SELL_MOVING_AVG_FACT);



    """

showBuySellMovingAverageFact = """SELECT * FROM buy_sell_moving_avg_fact"""

# Create table for getting list of buy sell symbols for each day
createTableBuySellSymbols = """
CREATE TABLE IF NOT EXISTS  buy_sell_symbols
(
	date_ DATE,
	buy_symbol VARCHAR(5000),
	sell_symbol VARCHAR(5000)
);
"""

# Truncate data from buy sell symbols table
truncateTableBuySellSymbols = """
TRUNCATE TABLE buy_sell_symbols;
"""

# need to execute this as group concat function has length of minimum 1024 only
expand_symbol_data_length = """SET LOCAL group_concat_max_len = 1000000;"""

# This query calculates daily buy sell symbols with respect to date
# Source table :- buy sell moving average fact
# Target table :- buy sell symbols
calculateBuySellSymbols = """

                        INSERT INTO BUY_SELL_SYMBOLS
                        WITH CTE0 AS(
                        SELECT MAX(DS.DATE_) AS MAX_DT 
                        FROM BUY_SELL_MOVING_AVG_FACT DS
                        ),
                        CTE AS (
                        SELECT DATE_,SYMBOL,
                        CASE 
                            WHEN BUY_SIGNAL != "" THEN SYMBOL 
                        END AS BUYS,
                        CASE 
                            WHEN SELL_SIGNAL != "" THEN SYMBOL 
                        END AS SELLS
                        FROM BUY_SELL_MOVING_AVG_FACT
                        WHERE BUY_SIGNAL != "" OR SELL_SIGNAL != ""
                        AND DATE_ BETWEEN (SELECT DATE_SUB(CTE0.MAX_DT, INTERVAL 60 DAY) FROM CTE0) AND (SELECT MAX_DT FROM CTE0)
                        )
                        SELECT DATE_,
                        GROUP_CONCAT(BUYS ORDER BY SYMBOL ASC )AS BUY_SYMBOL,
                        GROUP_CONCAT(SELLS ORDER BY SYMBOL ASC) AS SELL_SYMBOL
                        FROM CTE
                        WHERE DATE_ > (SELECT MAX(DATE_) FROM BUY_SELL_SYMBOLS)
                        GROUP BY DATE_
                        ORDER BY DATE_ ASC;

"""

showBuySellSymbols = """SELECT * FROM buy_sell_symbols"""
