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

truncateTableDailyGainersLosers = """
TRUNCATE TABLE gainers_losers;
"""

calculateDailyGainersLosers = """
                      
                       INSERT INTO GAINERS_LOSERS
                       SELECT SYMBOL_ID, DATE_, SYMBOL, SERIES, RESULT_, RANKERS FROM 
                       (
                       SELECT * FROM (
                       SELECT SYMBOL_ID, DATE_, SYMBOL,SERIES,RESULT_,
                               CASE 
                                   WHEN RESULT_ > 0 THEN RANK() OVER(ORDER BY RESULT_ DESC) 
                                   WHEN RESULT_ <= 0 THEN RANK() OVER(ORDER BY RESULT_  ASC ) 
                               END AS RANKERS,
                              RANK() OVER (ORDER BY RESULT_) AS RANK_LOSERS,
                              RANK() OVER(ORDER BY RESULT_ DESC) AS RANK_GAINERS
                       FROM (
                           SELECT *, 
                                  COALESCE(((TODAY_PRICE - LAST_PRICE) / NULLIF(LAST_PRICE,0)) * 100, 0) AS RESULT_
                           FROM (
                               SELECT *, 
                                      LAG(CLOSE_) OVER (PARTITION BY SYMBOL ORDER BY DATE_) AS LAST_PRICE,
                                      CLOSE_ AS TODAY_PRICE
                               FROM DAILY_FACT_STOCK
                           ) AS SUB
                       ) AS SUB2
                       WHERE DATE_ = CURRENT_DATE() 
                       ) AS SUB3 
                       WHERE RANK_GAINERS BETWEEN 1 AND 5 OR RANK_LOSERS BETWEEN 1 AND 5
                       ) AS SUB4
                       ORDER BY RESULT_ DESC,RANKERS;

   """