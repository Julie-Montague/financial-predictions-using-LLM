import os
import pandas as pd
from tqdm import tqdm
import re
from openai import OpenAI

#2. Process Market information
client = OpenAI(api_key="")

def GPT_analysis(sentence):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages = [
                { "role": "system", "content": "You are a helpful assistant." },
                {"role":"user",
                        "content":f"Decide whether a newsheadline's sentiment is positive, neutral, or negative, and provide a confidence score (0-100)\n\nnewsheadline: \"{sentence}\"\nSentiment:"}],
            temperature=0,
            max_tokens=60,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0
            )
        output = response.choices[0].message.content.strip()
        print(output)

        #parse sentiment and confidence
        sentiment ,confidence = None,None
        sentiment_match = re.search(r"Sentiment:\s*(positive|neutral|negative)",output,re.IGNORECASE)
        confidence_match = re.search(r"Confidence Score:\s*(\d+)",output)

        if sentiment_match:
            sentiment = sentiment_match.group(1)
        if confidence_match:
            confidence = int(confidence_match.group(1))
        return {"sentiment":sentiment,"confidence":confidence}

    except Exception as e:
        print(f"Error processing: {sentence}\n {e}")
        return {"Sentiment": None, "Confidence": None}

# Folder path containing the target CSV files
NASDAQinput = "Output/S&P"
NASDAQoutput = "Output/S&P_GPT"
if not os.path.exists(NASDAQoutput):
    os.makedirs(NASDAQoutput)
    

# Folder path containing the ft CSV files
#today = datetime.datetime.today()
today = pd.to_datetime('2025-01-28')
today = today.strftime("%Y-%m-%d")
marketInput = f"Output/{today}/market/ft"
marketOutput = f"Output/{today}/market/GPT"
if not os.path.exists(marketOutput):
    os.makedirs(marketOutput)

# Iterate through the files in the folder

def GPT_analysis_for_folder(inputpath, outputpath): 
    try:
        print("---os input path",os.listdir(inputpath))
        for filename in tqdm(os.listdir(inputpath)):
            if filename.endswith(".csv"):
                print("-------------------------FILE NAME",filename)
                file_path = os.path.join(inputpath, filename)
                print(f'start processing {file_path}')
                
                # Read the CSV file
                df = pd.read_csv(file_path)

                if df.empty:
                    continue
                else:
                    # Get the column names that end with "_Title" or "_Subtitle"
                    relevant_columns = [col for col in df.columns if col.endswith(("_Titles", "_Subtitles"))]
                    print(f'relevant_columns are {relevant_columns}')
                    
                    # Apply GPT_process() to relevant columns
                    for column in relevant_columns:
                        sentiment_column = column + "_GPT_SENTIMENT"
                        confidence_column  = column + "_GPT_SCORE"

                        if sentiment_column in df.columns and confidence_column in df.columns:
                            print(f"skipping already processed columns : {sentiment_column},{sentiment_column}")
                            continue
                        else:
                            df[[sentiment_column,confidence_column]] = df[column].apply(
                                lambda x : pd.Series(GPT_analysis(str(x))) if pd.notnull(x)
                                else pd.Series({"sentiment":None,"confidence":None})
                            )
                    
                    # Save the updated DataFrame to a new file
                    df.to_csv(f'{outputpath}/{filename}', index=False)
                    print(f'{filename} saved')
            print(f'{inputpath} finished')
    except Exception as e:
        print(f"Error : {e}")
            
if __name__ == "__main":  
    GPT_analysis_for_folder(NASDAQinput, NASDAQoutput)
    GPT_analysis_for_folder(marketInput, marketOutput)
  