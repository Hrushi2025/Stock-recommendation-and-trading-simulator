# This query 
createTableBuySellSymbols = """
CREATE TABLE IF NOT EXISTS  buy_sell_symbols
(
	date_ DATE,
	buy_symbol VARCHAR(5000),
	sell_symbol VARCHAR(5000)
);
"""


truncateTableBuySellSymbols = """
TRUNCATE TABLE buy_sell_symbols;
"""


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
