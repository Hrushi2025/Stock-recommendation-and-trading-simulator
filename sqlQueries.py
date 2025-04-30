# This is the main program that executes each table queries that are taken from config Files from configFiles folder

from Project.configFiles.dbConfig import conn
from Project.configFiles.movingAverageConfig import calculateMovingAverage
from Project.configFiles.rsiIndexConfig import calculateRsiIndex
from Project.configFiles.dailyGainersLosersConfig import calculateDailyGainersLosers
from Project.configFiles.buySellMovingAverageConfig import calculateBuySellMovingAverage
from Project.configFiles.buySellSymbolsConfig import calculateBuySellSymbols

cursor = conn.cursor()

cursor.execute(calculateMovingAverage)
conn.commit()

cursor.execute(calculateRsiIndex)
conn.commit()

cursor.execute(calculateDailyGainersLosers)
conn.commit()

cursor.execute(calculateBuySellMovingAverage)
conn.commit()

cursor.execute(calculateBuySellSymbols)
conn.commit()


cursor.execute()