# Config file for generating buy sell alarm from the moving average calculation

# Creating the buy_sell_moving_avg_fact table
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
# Source tables :- daily_fact_stock , moving_average_fact
# Target tables :- buy_sell_moving_average_fact
calculateBuySellMovingAverage = """
                    INSERT INTO BUY_SELL_MOVING_AVG_FACT
                    WITH CTE AS(
                                    SELECT MAX(DS.DATE_) AS MAX_DT 
                                    FROM DAILY_FACT_STOCK DS
                                    ),
                    CTE2 AS (
                    SELECT RANK_, DATE_, SYMBOL, CLOSE_, AVG_7_DAYS,AVG_14_DAYS, 
                    RES.RESS,LAG(RES.RESS) OVER(PARTITION BY SYMBOL ORDER BY DATE_) AS LAG_7_DAYS,
                    CASE 
                        WHEN RES.RESS > 100 AND LAG(RES.RESS) OVER(PARTITION BY SYMBOL ORDER BY DATE_) < 100  AND RES.RESS > LAG(RES.RESS) OVER(PARTITION BY SYMBOL ORDER BY DATE_) THEN "BUY" ELSE ""
                    END AS BUY_SIGNAL,
                    CASE 
                        WHEN RES.RESS < 100 AND LAG(RES.RESS) OVER(PARTITION BY SYMBOL ORDER BY DATE_) > 100 AND RES.RESS < LAG(RES.RESS) OVER(PARTITION BY SYMBOL ORDER BY DATE_) THEN "SELL" ELSE ""
                    END AS SELL_SIGNAL
                    FROM 
                    (SELECT *,
                    (AVG_7_DAYS / AVG_14_DAYS) * 100 AS RESS 
                    FROM MOVING_AVERAGE_FACT MF) AS RES
                    WHERE DATE_ BETWEEN (SELECT DATE_SUB(CTE.MAX_DT, INTERVAL 60 DAY) FROM CTE) AND (SELECT MAX_DT FROM CTE)
                    )
                    SELECT * FROM CTE2
                    WHERE DATE_ > (SELECT MAX(DATE_) FROM BUY_SELL_MOVING_AVG_FACT);


    """