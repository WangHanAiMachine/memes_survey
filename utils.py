import sqlite3
import time, datetime
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, storage

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn



def sampleQuestion(userId):
    conn = get_db_connection()
    questionsStatus = conn.execute('SELECT * FROM questionsStatus WHERE userId = ?', (userId,)).fetchall()
    modelId = -1
    contextId = -1
    memeId = -1
    annotationId = -1
    startTime = int(time.time())
    for record in questionsStatus:
        if(int(record["annotated"]) == 0):
            modelId = record["modelId"]
            contextId = record["contextId"]
            memeId = record["memeId"]
            annotationId = record["annotationId"]
            break

    if(modelId >0 and contextId > 0 and memeId > 0 and annotationId > 0):
        conn.execute('UPDATE questionsStatus SET annotated = ?'
                            ' WHERE modelId = ? AND contextId = ? AND memeId = ? AND annotationId = ?',
                            (1, modelId, contextId, memeId, annotationId))

        conn.execute("INSERT INTO inprogress (modelId, contextId, memeId, annotationId, startTime) VALUES (?, ?, ?, ?, ?)",
                (modelId, contextId, memeId, annotationId, startTime)
                )
        conn.commit()
        conn.close()
    return modelId, contextId, memeId, annotationId, startTime


def get_unannotated_memes(userId):
    conn = get_db_connection()
    questionsStatus = conn.execute('SELECT * FROM questionsStatus WHERE userId = ?', (userId,)).fetchall()
    total = 0
    un_annotated = 0
    for record in questionsStatus:
        total += 1
        if(int(record["annotated"]) == 0):
            un_annotated += 1
    return str(un_annotated) + " out of " + str(total) 

def text_retriever(modelId, contextId, memeId):
    model_list = ["ChatGPT", "LLaMA", "LLaVA", "Dank"]
    context_list = ["Causes", "Consequences", "Solutions", "Evidence of Absence", "Benefits"]
    support = {"Causes": "Supporter", "Consequences":"Supporter", "Solutions":"Supporter", "Evidence of Absence":"Denier", "Benefits":"Denier"}
    cot = {"ChatGPT":"COT", "LLaMA":"COT", "LLaVA":"Non-COT", }
    model = model_list[modelId - 1]
    context = context_list[contextId - 1]

    memes = pd.read_csv("questionBank/meme.csv")
    id = (contextId - 1) * 200 + memeId
    img_name =  memes["Image_Name"][id - 1]
    stored_memeId = memes["Image_ID"][id - 1]
    if(stored_memeId != memeId):
        print("Error: retrieve wrong image.")
    
    caption_path = "questionBank/meme_image_dataset/imgflip_"+ model  + "/"
    if(model == "Dank"):
        caption_path += "dank_learning_caption.json"
    else:
        caption_path += "climate_change_"+support[context]+"_"+context+"_" +cot[model] + "_caption.json"
    with open(caption_path, "r") as f:
        captions = json.load(f)
    caption = captions[img_name][0]
    return caption.replace("<->", "-")

def meme_retriever(modelId, contextId, memeId):
    model_list = ["ChatGPT", "LLaMA", "LLaVA", "Dank"]
    context_list = ["Causes", "Consequences", "Solutions", "Evidence of Absence", "Benefits"]
    support = {"Causes": "Supporter", "Consequences":"Supporter", "Solutions":"Supporter", "Evidence of Absence":"Denier", "Benefits":"Denier"}
    cot = {"ChatGPT":"COT", "LLaMA":"COT", "LLaVA":"Non-COT", }
    model = model_list[modelId - 1]
    context = context_list[contextId - 1]
    memes = pd.read_csv("questionBank/meme.csv")
    
    id = (contextId - 1) * 200 + memeId
    img_name =  memes["Image_Name"][id - 1]
    stored_memeId = memes["Image_ID"][id - 1]
    if(stored_memeId != memeId):
        print("Error: retrieve wrong image.")
    
    caption_path = "questionBank/meme_image_dataset/imgflip_"+ model  + "/"
    if(model == "Dank"):
        caption_path += "memes/"
    else:
        caption_path += context.replace(" ", "_") + "_" + cot[model] + "/"
    img_path = caption_path + img_name.replace("/" , "") + ".jpg"
    destination_path = "images/"  + img_name.replace("/" , "") + ".jpg"
    image_url = check_and_upload_image(img_path, destination_path)
    return image_url

def submitQuestion(userId, modelId, contextId, memeId, annotationId, hilarity_text, support_text, similar_meme,\
                   hateful_meme, hilarity_meme, support_meme, persuasiveness, startTime):
    conn = get_db_connection()
    cur_time = time.time()
    cur_time_format = datetime.datetime.fromtimestamp(cur_time).strftime('%Y-%m-%d %H:%M:%S')
    startTime = datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')

    conn.execute('DELETE FROM inprogress WHERE modelId = ? AND contextId = ? AND memeId = ? AND annotationId = ?', (modelId, contextId, memeId, annotationId))
    conn.execute('UPDATE questionsStatus SET annotated = ?'
                    ' WHERE  userId = ? AND modelId = ? AND contextId = ? AND memeId = ? AND annotationId = ?', 
                    (1, userId, modelId, contextId, memeId, annotationId))

    conn.execute("INSERT INTO submitted (modelId, contextId, memeId, annotationId, startTime, end_time, hilarity_text, support_text, similar_meme, hateful_meme, hilarity_meme, support_meme, persuasiveness) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (modelId, contextId, memeId, annotationId, startTime, cur_time_format, hilarity_text, support_text, similar_meme, hateful_meme, hilarity_meme, support_meme, persuasiveness)
            )
    conn.commit()
    conn.close()

def closeSurvey(modelId, contextId, memeId, annotationId):
    conn = get_db_connection()
    
    conn.execute('DELETE FROM inprogress WHERE modelId = ? AND contextId = ? AND memeId = ? AND annotationId = ?', (modelId, contextId, memeId, annotationId))
    conn.execute('UPDATE questionsStatus SET annotated = ?'
                    ' WHERE modelId = ? AND contextId = ? AND memeId = ? AND annotationId = ?', 
                    (0, modelId, contextId, memeId, annotationId))

    conn.commit()
    conn.close()

def check_and_upload_image(image_path, destination_path):
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': "aaaimemegeneration.appspot.com"
        })

    bucket = storage.bucket()
    
    # Check if the image already exists
    blob = bucket.blob(destination_path)
    if blob.exists():
        print("Image already exists in Firebase Storage.")
        img_url = "https://storage.googleapis.com/" + bucket.name  + "/" +blob.name
        print(img_url)
        return blob.public_url
    
    # If image doesn't exist, upload it
    try:
        blob.upload_from_filename(image_path)
        print("Image uploaded successfully.")
        img_url = "https://storage.googleapis.com/" + bucket.name + "/" +blob.name
        print(img_url)
        return blob.public_url
    except Exception as e:
        print("Error uploading image:", e)
        return None
    
