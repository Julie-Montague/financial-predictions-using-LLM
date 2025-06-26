from base_file.base import Properties as props
import pandas as pd
from tqdm import tqdm
import os
import re

#specify path files
stockInput = props.stockInput
stockOutput = props.stockOutput
stockOutput1 = props.stockOutput1

marketInput = props.marketInput
marketOutput = props.marketOutput
marketOutput1 = props.marketOutput1

def GPT_analysis(sentence):
    try:
        client = props.client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages = [
                { "role": "system", "content": "You are a helpful assistant." },
                {"role":"user",
                        "content":f"Decide whether a newsheadline's sentiment is positive, neutral, or negative, and provide a confidence score between 0 and 1 to 17 decimal places like the finBert model\n\nnewsheadline: \"{sentence}\"\nSentiment:"}],
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
        confidence_match = re.search(r"Confidence Score:\s*([\d.]+)",output)

        if sentiment_match:
            sentiment = sentiment_match.group(1).lower()
        if confidence_match:
            confidence = float(confidence_match.group(1))
        return {"sentiment":sentiment,"confidence":confidence}

    except Exception as e:
        print(f"Error processing: {sentence}\n {e}")
        return {"sentiment": None, "confidence": None}

#2. Process Market information 
class GPT: 
    def GPT_analysis_for_folder(self,inputpath, outputpath,outputpath1): 
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
                        #df = df.head(6)
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
                                    lambda x : pd.Series(GPT.GPT_analysis(str(x))) if pd.notnull(x)
                                    else pd.Series({"sentiment":None,"confidence":None})
                                )

                                print(df.info())
                                df.columns = df.columns.str.upper()
                                print(df.columns)

                                #save file all scores
                                df.to_csv(f'{outputpath1}/{filename}', index=False)
                                #svae file with only gpt score
                                df1 = df.drop(['titles_finBERTLabel','titles_finBERTScore','subtitles_finBERTLabel','subtitles_finBERTScore'],axis=1)
                                df1.to_csv(f'{outputpath}/{filename}', index=False)
                                print(f'{filename} saved')
            print(f'{inputpath} finished')           
        except Exception as e:
            print(f"Error : {e}")