import sqlite3
import pandas as pd

# Model
# 1 - ChatGPT
# 2 - LLaMA
# 3 - LLaVA
# 4 - Dank

# Context
# 1 - Causes
# 2 - Consequences
# 3 - Solutions
# 4 - Evidence of Absence
# 5 - Benefits

# User
# 1 - sarahwf77
# 2 - llester_leong
# 3 - after232
# 4 - colinteoh
# 5 - Seannny
# 6 - shaunnope
# 7 - samuellam123
# 8 - Spacedogcat
# 9 - raynardzxc
# 10 - geneeliaw
# 11 - itsskiip
# 12 - han


# python3 init_db.py

# To run
# nohup python3 app.py
# To stop
# lsof -t -i tcp:8000 | xargs kill -9

# python3 save_db.py

cur_stage = 1 # 1 ~ 5
stages_annotation = [0, 40, 80, 120, 160, 200]
if(cur_stage == 1):
    total_annotators = 12
    annotation_per_stage = 40 * 2 * 5 * 4 // total_annotators 
else:
    total_annotators = 11
    annotation_per_stage = 40 * 2 * 5 * 3 // total_annotators 
demo_size = list( range(stages_annotation[cur_stage - 1] + 1, stages_annotation[cur_stage] + 1))

model_size = list(range(1, 5))
context_size = list(range(1, 6))
annotation_size = list(range(1, 3))

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    conn = sqlite3.connect('database.db', isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM submitted", conn)
    db_df.to_csv('questionAnswer/submitted' + str(cur_stage)  + '.csv', index=False)
    conn.close()
    connection.executescript(f.read())

cur = connection.cursor()

g = 1
accumulated_size = 0
for i in model_size:
    for j in context_size:
        for z in annotation_size:
            for k in demo_size:
                if(i == 4 and k >= 41):
                    break
                # accumulated_size += 1
                # if(accumulated_size > annotation_per_stage and g < total_annotators):
                #     accumulated_size = 1
                #     g += 1

                cur.execute("INSERT INTO questionsStatus (modelId, contextId, memeId, annotationId, userId) VALUES (?, ?, ?, ?, ?)",
                    (i, j, k, z, g)
                    )
                if(g < total_annotators):
                    g += 1
                else:
                    g = 1
            
connection.commit()
connection.close()
