import sqlite3
import pandas as pd
from init_db import cur_stage

conn = sqlite3.connect('database.db', isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)

db_df = pd.read_sql_query("SELECT * FROM submitted", conn)
db_df.to_csv('questionAnswer/submitted' + str(cur_stage) +'.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM inprogress", conn)
db_df.to_csv('questionAnswer/inprogress.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM questionsStatus", conn)
db_df.to_csv('questionAnswer/questionsStatus.csv', index=False)

conn.close()