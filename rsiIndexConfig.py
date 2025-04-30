
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

truncateTableRsiIndexFact = """
TRUNCATE TABLE rsi_index_fact;
"""

calculateRsiIndex = f"""
            
                INSERT INTO RSI_INDEX_FACT
                 WITH CTE0 AS(
                                SELECT MAX(DS.DATE_) AS MAX_DT 
                                FROM DAILY_FACT_STOCK DS
                ),
                CTE AS (
                    SELECT 
                        TD.RANK_,
                        DS.DATE_, 
                        DS.SYMBOL, 
                        DS.CLOSE_, 
                        DS.CLOSE_ AS LAST_DATE_PRICE, 
                        LEAD(DS.CLOSE_, 1) OVER (PARTITION BY DS.SYMBOL ORDER BY DS.DATE_) AS CURR_DATE_PRICE
                    FROM 
                        MOVING_AVERAGE_FACT DS
                        JOIN TRADING_DIMENSION TD ON TD.DATE_ = DS.DATE_
                        WHERE DS.DATE_ BETWEEN (SELECT DATE_SUB(CTE0.MAX_DT, INTERVAL 60 DAY) FROM CTE0) AND (SELECT MAX_DT FROM CTE0)
                ),
                CTE2 AS (
                    SELECT 
                        *, 
                        (CURR_DATE_PRICE - LAST_DATE_PRICE) AS CHANGED,
                        CASE 
                            WHEN CURR_DATE_PRICE - LAST_DATE_PRICE < 0 
                            THEN ABS(CURR_DATE_PRICE - LAST_DATE_PRICE)  
                            ELSE 0 
                        END AS LOSS,
                        CASE 
                            WHEN CURR_DATE_PRICE - LAST_DATE_PRICE > 0 
                            THEN CURR_DATE_PRICE - LAST_DATE_PRICE 
                            ELSE 0 
                        END AS GAIN
                    FROM 
                        CTE
                ),
                CTE3 AS (
                    SELECT 
                        *,
                        AVG(GAIN) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS AVG_GAIN_7,
                        AVG(LOSS) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS AVG_LOSS_7,
                        AVG(GAIN) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS AVG_GAIN_14,
                        AVG(LOSS) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS AVG_LOSS_14,
                        AVG(GAIN) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS AVG_GAIN_21,
                        AVG(LOSS) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS AVG_LOSS_21,
                        AVG(GAIN) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) AS AVG_GAIN_28,
                        AVG(LOSS) OVER (PARTITION BY SYMBOL ORDER BY DATE_ ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) AS AVG_LOSS_28
                    FROM 
                        CTE2
                ),
                CTE4 AS (
                    SELECT 
                        *,
                        COALESCE((AVG_GAIN_7 / NULLIF(AVG_LOSS_7, 0)), 0) AS RS_7,
                        COALESCE((AVG_GAIN_14 / NULLIF(AVG_LOSS_14, 0)), 0) AS RS_14,
                        COALESCE((AVG_GAIN_21 / NULLIF(AVG_LOSS_21, 0)), 0) AS RS_21,
                        COALESCE ((AVG_GAIN_28 / NULLIF(AVG_LOSS_28, 0)), 0) AS RS_28
                    FROM 
                        CTE3
                )
                SELECT 
                    *,
                    COALESCE(100 - (100 / (1 + RS_7)), 0) AS RSI_7,
                    COALESCE(100 - (100 / (1 + RS_14)), 0) AS RSI_14,
                    COALESCE(100 - (100 / (1 + RS_21)), 0) AS RSI_21,
                    COALESCE(100 - (100 / (1 + RS_28)), 0) AS RSI_28
                FROM 
                    CTE4
                    WHERE DATE_ > (SELECT MAX(DATE_) FROM RSI_INDEX_FACT );
            """