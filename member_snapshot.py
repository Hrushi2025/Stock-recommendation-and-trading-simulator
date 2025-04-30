from datetime import timedelta, datetime

from dbConfig import conn

cursor = conn.cursor()


def gettradingDates():
    cursor.execute("SELECT date_ FROM trading_dimension")

    dates = cursor.fetchall()

    tradeDates = [item[0] for item in dates]

    return tradeDates


def getStartDate():

    cursor.execute("SELECT max(date_) FROM member_snapshot")

    date = cursor.fetchall()

    return date

def getEndDate():

    cursor.execute("SELECT max(date_) from member_buy_sell")

    date = cursor.fetchall()

    return date


def memberSnapshot():
    data  = cursor.execute("""
    
INSERT INTO member_snapshot 
WITH cte1 AS
(
	(SELECT
		mbs.date_ AS mbs_date,
		mbs.member_id AS mbs_member_id,
		mbs.symbol AS mbs_symbol,
		mbs.buy_sell AS mbs_buy_sell,
		mbs.close_ AS mbs_close,
		mbs.qty AS mbs_qty,
		ms.date_,
		ms.member_id,
		ms.symbol,
		ms.buy_sell,
		ms.close_,
		ms.qty,
		ms.invested_deducted,
		ms.remaining_qty,
        ms.total_buy_qty AS prev_total_buy_qty,
        ms.total_sell_qty AS prev_total_sell_qty,
        ms.current_price,
		ms.average_price,
		ms.current_invested,
		ms.total_investment AS prev_total_investment,
		ms.total_sell AS prev_total_sell,
		ms.profit,
		ms.net_profit
	FROM member_buy_sell mbs
	LEFT JOIN member_snapshot ms
	ON COALESCE((SELECT next_day FROM temp_day WHERE current_day = ms.date_),ms.date_ + INTERVAL 1 day) = mbs.date_
	AND ms.member_id = mbs.member_id
	AND ms.symbol = mbs.symbol
	WHERE mbs.date_ =  COALESCE((SELECT next_day FROM temp_day WHERE current_day =  (SELECT max(date_) FROM member_snapshot)) ,'2023-01-12')
)
	UNION
(	
	SELECT
		mbs.date_ AS mbs_date,
		mbs.member_id AS mbs_member_id,
		mbs.symbol AS mbs_symbol,
		mbs.buy_sell AS mbs_buy_sell,
		mbs.close_ AS mbs_close,
		mbs.qty AS mbs_qty,
		ms.date_,
		ms.member_id,
		ms.symbol,
		ms.buy_sell,
		ms.close_,
		ms.qty,
		ms.invested_deducted,
		ms.remaining_qty,
        ms.total_buy_qty AS prev_total_buy_qty,
        ms.total_sell_qty AS prev_total_sell_qty,
        ms.current_price,
		ms.average_price,
		ms.current_invested,
		ms.total_investment AS prev_total_investment,
		ms.total_sell AS prev_total_sell,
		ms.profit,
		ms.net_profit
	FROM member_buy_sell mbs
	RIGHT JOIN member_snapshot ms
	ON COALESCE((SELECT next_day FROM temp_day WHERE current_day = ms.date_),ms.date_ + INTERVAL 1 day)  = mbs.date_
	AND  ms.member_id = mbs.member_id
	AND  ms.symbol = mbs.symbol
	WHERE ms.date_ = COALESCE ((SELECT current_day FROM temp_day WHERE current_day = (SELECT max(date_) FROM member_snapshot) ),"2023-01-11")
)
)
, cte2 AS (
	SELECT
		COALESCE(cte1.mbs_date, COALESCE((SELECT next_day FROM temp_day WHERE current_day = cte1.date_),cte1.date_ + INTERVAL 1 DAY) ) AS date_,
		COALESCE(cte1.mbs_member_id, cte1.member_id) AS member_id,
		COALESCE(cte1.mbs_symbol, cte1.symbol) AS symbol,
		cte1.mbs_buy_sell AS buy_sell,
		COALESCE(cte1.mbs_close,st.close_) AS close_,
		COALESCE(cte1.mbs_qty,0) AS qty,
		CASE
			WHEN mbs_buy_sell = "BUY" THEN (cte1.mbs_qty * cte1.mbs_close)
			WHEN mbs_buy_sell = "SELL" THEN -(cte1.mbs_qty * cte1.mbs_close)
			ELSE 0
		END AS invested_deducted,
		COALESCE(cte1.remaining_qty ,0) AS prev_remaining_qty,
        coalesce(cte1.prev_total_buy_qty,0) AS prev_total_buy_qty,
        coalesce(cte1.prev_total_sell_qty,0) AS prev_total_sell_qty,
        cte1.current_price as current_price,
		cte1.average_price AS average_price,
		cte1.current_invested AS current_invested,
		COALESCE(cte1.prev_total_investment,0) AS prev_total_investment,
		COALESCE(cte1.prev_total_sell,0) AS prev_total_sell,
		COALESCE(cte1.profit,0) AS profit,
		COALESCE(cte1.net_profit,0) AS net_profit
	FROM cte1
	LEFT JOIN stock_daily_staging st
	ON st.date_  =  COALESCE((SELECT next_day FROM temp_day WHERE current_day = cte1.date_),cte1.date_ + INTERVAL 1 DAY)
	AND st.symbol = cte1.symbol
	)
, cte3 AS (	
	SELECT
		date_,
		member_id,
		symbol,
		buy_sell,
		close_,
		qty,
		invested_deducted,
		prev_remaining_qty,
		CASE
			WHEN buy_sell = "BUY" THEN (prev_remaining_qty + qty)
			WHEN buy_sell = "SELL" THEN (prev_remaining_qty - qty)
			ELSE prev_remaining_qty
		END AS remaining_qty,
        prev_total_buy_qty,
        prev_total_sell_qty,
        current_price,
		CASE
			WHEN buy_sell= "BUY" THEN  (((prev_remaining_qty * COALESCE(average_price,0)) + (qty * close_)) / (prev_remaining_qty + qty))
			ELSE average_price	
		END AS average_price,
		prev_total_investment,
		prev_total_sell,
		profit,
		net_profit
	FROM cte2)
SELECT
		date_,
		member_id,
		symbol,
		buy_sell,
		close_,
		qty,
		invested_deducted,
		prev_remaining_qty,
		remaining_qty,
        case 
			when buy_sell = "buy" then (qty + prev_total_buy_qty)
            else prev_total_buy_qty
		end as total_buy_qty,
        case 
			when buy_sell = "sell" then (qty + prev_total_sell_qty)
            else prev_total_sell_qty
		end as total_sell_qty,        
        (remaining_qty * close_) as current_price,
		average_price,
		(average_price * remaining_qty) AS current_invested,
		CASE
			WHEN buy_sell = "BUY" THEN (qty * close_) + prev_total_investment
			ELSE prev_total_investment
		END AS total_investment,
		CASE
			WHEN buy_sell = "SELL" THEN (qty * close_) + prev_total_sell
			ELSE prev_total_sell
		END AS total_sell,
		(remaining_qty * (close_- average_price)) AS profit,
		-- net profit
		((CASE
			WHEN buy_sell = "SELL" THEN (qty * close_) + prev_total_sell
			ELSE prev_total_sell
		END) + (average_price * remaining_qty) + (remaining_qty * (close_ - average_price)) - (CASE
			WHEN buy_sell = "BUY" THEN (qty * close_) + prev_total_investment
			ELSE prev_total_investment
		END)) AS net_profit,
		current_timestamp
        from cte3;
    """)

    conn.commit()



def main():


    startDate = getStartDate()[0][0]
    endDate = getEndDate()[0][0]


    startDate += timedelta(days=1)


    dates = gettradingDates()

    print(dates)
    print(startDate,endDate)

    while startDate < endDate:
        if startDate in dates:
            print("inserting data for --- ",startDate)
            memberSnapshot()
        startDate += timedelta(days=1)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
