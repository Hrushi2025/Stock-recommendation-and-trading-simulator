
### This is stock project 

#### File Name's
###### Python Files (.py)

1) DbConnection.py :- It contains the program for connecting to the database which is used in other programs. 
2) calander_dimension.py :- It contains program for  inserting data in cal_dim table, holiday_dim and trading_dim table.
3) Member_dimension.py:- The file contains program for generating the member dimension table for the given csv file.
4) Symbol_dimension.py :- This program is for generating the teh symbol_dimension table.
5) New_Symbol_Adding.py :- When new symbol nse file is downloaded from nse site as csv this program merges the old and new symbols to create anew list of symbols.
6) Daily_Stock_Fact_Staging_data_generation.py :-  When new symbols list it is generated this program fetches the data for newly given symbols and insert it into the database Fact and Staging tables.
7) Stock_Avg :- This program is of generating the moving average of 7,14 and 21 days from the current date.
8) Stock_Sql_Queries :- This file contains the sql script for moving_average and rsi index.
9) Folder_File_creation :- The program consists of creating the folder of Y_M_D then the year(2023, 2024) folder then the month(jan, feb) folder in it and then date folder by dates (21-08-2024, 20-08-2024).

###### Csv Files (.csv)

1) Holiday_Dim.csv :- This file contains csv format Holiday, Date, Day downloaded from nse website
2) Member_Dimensions.csv :- This file contains the data of member_id, f-name, l-name 
3) new_nse_symbols.csv :- This file has newly added data of symbols from nse it needs to downloaded from nse site and given name like this
