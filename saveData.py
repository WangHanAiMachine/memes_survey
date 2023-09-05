import sqlite3
import pandas as pd

cur_stage = 1 # 1 ~ 5
conn = sqlite3.connect('database.db', isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)

db_df = pd.read_sql_query("SELECT * FROM submitted", conn)
db_df.to_csv('questionAnswer/submitted' + str(cur_stage) +'.csv')

db_df = pd.read_sql_query("SELECT * FROM inprogress", conn)
db_df.to_csv('questionAnswer/inprogress.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM questionsStatus", conn)
db_df.to_csv('questionAnswer/questionsStatus.csv', index=False)

conn.close()