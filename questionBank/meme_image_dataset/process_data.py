import json
import csv

with open("questionBank/meme_image_dataset/valid_image.json", "r") as f:
    data = json.load(f)

header = [["Context", "Image_ID", "Image_Name", "Selected_Dank"]]
count ={"LLM": 0, "Dank": 0}

for context in data:
    
    img_list = data[context][1]
    for img in img_list:
        # path = "/questionBank/meme_image_dataset/imgflip" + model + "/" + img.replace("/", "") + ".jpg"
        if(count["LLM"] < 200):
            count["LLM"] +=1
            if(count["Dank"] < 40):
                count["Dank"] +=1
                header.append( [context, count["LLM"], img, True] )
            else:
                header.append( [context, count["LLM"], img, False] )
        else:
            count["LLM"] = 0
            count["Dank"] = 0
            break

filename = "questionBank/meme.csv"
with open(filename, mode='w') as file:
    writer = csv.writer(file)
    # Write the data to the CSV file
    writer.writerows(header)