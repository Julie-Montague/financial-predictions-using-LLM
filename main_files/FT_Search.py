from base_file.base import Properties as props
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from transformers import pipeline
from transformers import BertTokenizer,BertForSequenceClassification
import requests 
import os
import glob
import re

# 4. Iterate through Target Tickers 
class individual_data:
    
    def __init__(self, Name, Ticker,search_company):
        self.search_co = search_company
        self.name = Name
        self.ticker = Ticker
        self.today = props.calc_date
        self.page_range = props.pagestockRange
        self.output_path = props.outputPath
        self.allstockOutput = props.allstockOutput

    def fetch_url(self,url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def get_FT_search_Init(self):
            try:
                query = self.ticker
                search_co = self.search_co
                print(f'starting initialise {query}')
                finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
                tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
                nlp = pipeline('sentiment-analysis', model=finbert, tokenizer=tokenizer)
                Search_titles=[]
                Search_Subtitles=[]
                Search_dates =[]

                Search_titles_finBERTLabel =[]
                Search_titles_finBERTScore =[]
                Search_Subtitles_finBERTLabel =[]
                Search_Subtitles_finBERTScore =[]

                for page in tqdm(range(1,self.page_range)):
                    url="https://www.ft.com/search?q={}&page={}".format(search_co,page)
                    response = self.fetch_url(url)
                    
                    if response is None:
                        continue
                    
                    soup=BeautifulSoup(response, "lxml")
                    
                    soup = soup.find("ul", {'class': 'search-results__list'})

                    if soup == None:
                        continue
                    else:
                        
                        for Card in soup.findAll("li",{"class":"search-results__list-item"}):
                            
                            if Card ==None:
                                continue
                            else:
                                    
                                title = Card.find("div",{"class":"o-teaser__heading"})
                                print(title.text)
                                if title == None:
                                    Search_titles.append('none')
                                    Search_titles_finBERTLabel.append(0)
                                    Search_titles_finBERTScore.append(0)
                                else:
                                    titles=title.text
                                    Search_titles.append(titles)
                                    Search_titles = [str(di) if di is None else di for di in Search_titles]
                                    Search_titles_finBERTresults = nlp(titles)
                                    for items in Search_titles_finBERTresults:
                                        Search_titles_finBERTLabel.append(items['label'])
                                        Search_titles_finBERTScore.append(items['score'])

                                Subtitle=Card.find("a",{"class":"js-teaser-standfirst-link"})
                                if Subtitle == None:
                                    Search_Subtitles.append('none')
                                    Search_Subtitles_finBERTLabel.append(0)
                                    Search_Subtitles_finBERTScore.append(0)
                                else:
                                    titles=Subtitle.text
                                    Search_Subtitles.append(titles)
                                    Search_Subtitles = [str(di) if di is None else di for di in Search_Subtitles]
                                    World_Subtitles_finBERTresults = nlp(titles)
                                    for items in World_Subtitles_finBERTresults:
                                        Search_Subtitles_finBERTLabel.append(items['label'])
                                        Search_Subtitles_finBERTScore.append(items['score'])

                                Date=Card.find("time",{"class":"o-teaser__timestamp-date"})
                                if Date == None:
                                    Search_dates.append('none')
                                else:
                                    Dates=Date.get('datetime')
                                    Search_dates.append(Dates)

                df = pd.DataFrame({'Date': Search_dates, 
                                f'{query}_FT_Titles': Search_titles, 
                                f'{query}_FT_Subtitles': Search_Subtitles, 
                                'titles_finBERTLabel': Search_titles_finBERTLabel, 
                                'titles_finBERTScore': Search_titles_finBERTScore, 
                                'Subtitles_finBERTScore': Search_Subtitles_finBERTScore, 
                                'Subtitles_finBERTLabel':Search_Subtitles_finBERTLabel
                                })

                df.to_csv(f'{props.stockInput}/ft_{query}.csv', index=False)
                print(f'({query} saved')
            except Exception as e:
                print(f"Error : {e}")

    def get_Combined_Sections(self):
        try:
            combined_data =[]
            cols = ['DATE','TITLE','SUBTITILE','COMPANY']
            path_f = f'{self.output_path}/search/FinBert'
            #identify all CSV files
            all_files = glob.glob(os.path.join(path_f,'*.csv'))


            for file_path in all_files:
                df = pd.read_csv(file_path)
                if df.empty:
                    continue
                else:
                    match = re.search(r"search[\\/].*?[\\/](ft_[^,]+)",file_path)
                    if match:
                        extracted_match = match.group(1)
                        df['COMPANY'] = extracted_match
                    else:
                        print("No match found")

                    df1 = df.drop(['titles_finBERTLabel','titles_finBERTScore','Subtitles_finBERTLabel',          'Subtitles_finBERTScore'],axis=1)
                    print(df1.head(3))
                    df1.columns = cols
                    combined_data.append(df1)
            if len(combined_data) == 1:
                combined_df = combined_data[0]  # No need to concatenate
            else:
                combined_df = pd.concat(combined_data, ignore_index=True)
            print(combined_df.head(3))
            print(combined_df.shape)

            combined_df.to_csv(f'{self.allstockOutput}/all_articles.csv', index=False)

        except Exception as e:
                print(f"Error : {e}")
