# Stock-recommendation-and-trading-simulator
Stock Market Analysis System

Overview

This project is a Python-based stock market analysis system that processes historical and real-time stock data to generate trading signals, track member transactions, and maintain dimensional data for analysis. It uses MySQL as the database to store stock data, trading signals, and member activities. The system fetches data from Yahoo Finance (yfinance), processes it through SQL queries, and applies trading strategies based on moving averages and Relative Strength Index (RSI). It also manages member assignments to stock symbols and tracks their buy/sell activities.

The system is modular, with separate scripts for data ingestion, database operations, signal generation, and transaction processing. It supports daily updates and historical data processing, with a focus on generating actionable trading insights.

Prerequisites





Python 3.8+: Ensure Python is installed with the following libraries:





mysql-connector-python



pandas



yfinance



pymysql



MySQL Database: A MySQL server with a database named stock_project. Update the connection details in dbConfig.py.



CSV Files:





EQUITY_L.csv: Stock symbol data from the NSE website.



Holiday_Dim.csv: NSE holiday data for the relevant years.



Member_Dimensions.csv: Member data for the member_dimension table.



NSE Holiday Data: Download holiday CSV files for each year from the NSE website and update Holiday_Dim.csv accordingly.

Project Structure

The system consists of Python scripts and SQL configuration files organized into the following categories:





Database Setup and Connection:





dbConfig.py: Establishes a MySQL connection to the stock_project database.



Data Ingestion:





newSymbolsUpdate.py: Imports stock symbols from EQUITY_L.csv into symbol_staging and updates symbol_dimension_table.



dailyDataGen.py: Fetches daily stock data from Yahoo Finance and populates stock_daily_staging and stock_daily_fact tables.



Dimension Table Management:





calendarDimension.py: Generates calendar_dimension, holiday_dimension, and trading_dimension tables for date-related data.



memberDimension.py: Imports member data from Member_Dimensions.csv into member_dimension.



memberMappedSymbols.py: Assigns stock symbols to members and stores mappings in member_symbol_assignment.



Trading Signal Generation:





queriesConfig.py: Contains SQL queries for creating and populating tables like moving_average_fact, rsi_index_fact, gainers_losers, buy_sell_moving_avg_fact, and buy_sell_symbols.



movingAverageConfig.py, rsiIndexConfig.py, dailyGainersLosersConfig.py, buySellMovingAverageConfig.py, buySellSymbolsConfig.py: Individual configuration files with SQL queries for specific tables.



executeSqlQuery.py: Executes the SQL queries to generate trading signals.



sqlQueries.py: A main script that runs queries from the configuration files in sequence.



Member Transaction Processing:





memberBuySellOverMovingAvg.py: Processes member buy/sell transactions based on moving average signals (O(N³) complexity).



memberBuySellOverMovingAvgOptimized.py: An optimized version of the above with O(N²) complexity using a dictionary.



memberBuySellTest.py: A test version of the optimized script with modified data filtering.



member_snapshot.py: Generates snapshots of member transactions, tracking investments, profits, and quantities.



Data Cleanup:





removeFirstSell.py: Deletes "SELL" signals from buy_sell_moving_avg_fact that occur before a "BUY" for a symbol.



removeFirstSell1.py: A diagnostic version that identifies first "BUY" and "SELL" dates without modifying the database.

How the System Works

The system operates as a pipeline that ingests data, processes it, generates trading signals, and tracks member activities. Below is the workflow:





Database Setup:





dbConfig.py establishes a connection to the MySQL database stock_project.



Tables are created using SQL queries in queriesConfig.py and related config files (executed by executeSqlQuery.py or sqlQueries.py).



Dimension Data Population:





newSymbolsUpdate.py populates symbol_dimension_table with stock symbols from EQUITY_L.csv.



calendarDimension.py generates date-related dimension tables:





calendar_dimension: All dates with attributes like day, month, quarter, and weekend status.



holiday_dimension: NSE holidays from Holiday_Dim.csv.



trading_dimension: Trading days (excluding holidays and weekends) with ranks.



memberDimension.py loads member data into member_dimension.



memberMappedSymbols.py assigns 20 stock symbols to each member and stores mappings in member_symbol_assignment.



Daily Data Ingestion:





dailyDataGen.py fetches daily stock data from Yahoo Finance for all symbols in symbol_dimension.



Data is processed into stock_daily_staging (full data) and stock_daily_fact (subset for analysis) tables.



The script runs from the last recorded date in stock_daily_staging to the current date.



Trading Signal Generation:





sqlQueries.py or executeSqlQuery.py executes SQL queries to generate trading signals:





Moving Averages (moving_average_fact): Calculates 7, 14, 21, and 28-day moving averages using movingAverageConfig.py.



RSI (rsi_index_fact): Computes 7, 14, 21, and 28-day RSI values using rsiIndexConfig.py.



Daily Gainers/Losers (gainers_losers): Identifies top 5 gainers and losers based on daily price changes using dailyGainersLosersConfig.py.



Buy/Sell Signals (buy_sell_moving_avg_fact): Generates "BUY" or "SELL" signals based on the ratio of 7-day to 14-day moving averages using buySellMovingAverageConfig.py.



Buy/Sell Symbols (buy_sell_symbols): Aggregates buy/sell signals by date using buySellSymbolsConfig.py.



Queries only process new data by comparing the maximum date in target tables.



Data Cleanup:





removeFirstSell.py ensures valid buy/sell sequences by deleting "SELL" signals that occur before a "BUY" for a symbol.



removeFirstSell1.py is used for debugging to identify invalid sequences without modifying the database.



Member Transaction Processing:





memberBuySellOverMovingAvgOptimized.py (or its variants) processes buy/sell transactions for members based on signals in buy_sell_moving_avg_fact.



Transactions are recorded in member_buy_sell with random quantities (5-10 for buys, 1-5 for sells) and calculated values.



The optimized version uses a dictionary to map symbols to member IDs, reducing time complexity from O(N³) to O(N²).



member_snapshot.py generates daily snapshots in member_snapshot, tracking:





Remaining quantities, total buy/sell quantities, average price, current investment, total investment, total sell value, profit, and net profit.



Snapshots are created for trading days between the last snapshot date and the latest member_buy_sell date.

Running the System

To run the system, follow these steps:





Setup:





Install required Python libraries: pip install mysql-connector-python pandas yfinance pymysql.



Configure MySQL connection in dbConfig.py (update host, user, password, and database name).



Ensure CSV files (EQUITY_L.csv, Holiday_Dim.csv, Member_Dimensions.csv) are in the project directory.



Initialize Dimension Tables:





Run newSymbolsUpdate.py to populate symbol_dimension_table.



Run memberDimension.py to populate member_dimension.



Run calendarDimension.py to populate calendar_dimension, holiday_dimension, and trading_dimension. Update the start/end dates in the main() function and holiday CSV path as needed.



Run memberMappedSymbols.py to assign symbols to members.



Create Fact and Signal Tables:





Run executeSqlQuery.py with createTableQueries() uncommented to create tables defined in queriesConfig.py.



Ingest Daily Data:





Run dailyDataGen.py to fetch and store daily stock data. This should be scheduled daily to keep data up-to-date.



Generate Trading Signals:





Run sqlQueries.py or executeSqlQuery.py to execute queries for moving averages, RSI, gainers/losers, and buy/sell signals. Use truncateTableQueries() in executeSqlQuery.py if you need to clear existing data.



Clean Buy/Sell Signals:





Run removeFirstSell.py to remove invalid "SELL" signals. Use removeFirstSell1.py for debugging if needed.



Process Member Transactions:





Run memberBuySellOverMovingAvgOptimized.py to generate member transactions in member_buy_sell.



Run member_snapshot.py to create daily transaction snapshots in member_snapshot.



Scheduling:





Use a scheduler (e.g., cron or Python's schedule library) to automate daily runs of dailyDataGen.py, executeSqlQuery.py, removeFirstSell.py, memberBuySellOverMovingAvgOptimized.py, and member_snapshot.py.

Notes





Holiday Data: Update Holiday_Dim.csv annually with NSE holiday data, as calendarDimension.py relies on it for holiday_dimension.



Truncation: Be cautious with truncate queries in calendarDimension.py and executeSqlQuery.py. Uncomment them only when resetting tables.



Performance: The optimized memberBuySellOverMovingAvgOptimized.py is recommended for production due to its lower time complexity.



Error Handling: Add error handling in production to manage database connection issues or API failures in yfinance.



Data Validation: Validate CSV inputs and database outputs to ensure data integrity, especially for symbols and holidays.



Table Dependencies:





stock_daily_fact and trading_dimension are required for most signal generation queries.



buy_sell_moving_avg_fact depends on moving_average_fact.



buy_sell_symbols depends on buy_sell_moving_avg_fact.



member_buy_sell and member_snapshot depend on buy_sell_moving_avg_fact and member_symbol_assignment.
