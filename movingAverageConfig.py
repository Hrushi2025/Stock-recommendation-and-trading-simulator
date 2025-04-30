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

truncateTableMovingAverageFact = """

TRUNCATE TABLE moving_average_fact;

"""


calculateMovingAverage = f"""
            

                INSERT INTO MOVING_AVERAGE_FACT
                WITH CTE AS(
                SELECT MAX(DS.DATE_) AS MAX_DT 
                FROM DAILY_FACT_STOCK DS
                ),
                CTE2 AS (
                SELECT TD.RANK_ ,DS.DATE_, SYMBOL, CLOSE_,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS MOVING_AVG_7,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS MOVING_AVG_14,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS MOVING_AVG_21,
                            AVG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) AS MOVING_AVG_28
                            FROM DAILY_FACT_STOCK DS
                            JOIN TRADING_DIMENSION TD ON DS.DATE_ = TD.DATE_ 
                            WHERE DS.DATE_ BETWEEN (SELECT DATE_SUB(CTE.MAX_DT, INTERVAL 60 DAY) FROM CTE) AND (SELECT MAX_DT FROM CTE)
                )
                SELECT * FROM CTE2
                WHERE DATE_ > (SELECT MAX(DATE_) FROM MOVING_AVERAGE_FACT);

            """