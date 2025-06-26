from base_file.base import Properties as props
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from transformers import pipeline
from transformers import BertTokenizer,BertForSequenceClassification
import requests 
import time

class FinBert:
    def __init__(self):
        self.calc_date = props.calc_date
        self.sectionlist = props.sectionList
        self.page_range = props.pageRange
        self.output_path = props.outputPath
        self.market_data = props.marketInput
        self.allmarketInput = props.marketOutput1

    def Get_FT_Market(self):
            try:
                finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
                tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
                nlp = pipeline('sentiment-analysis', model=finbert, tokenizer=tokenizer)

                for section in tqdm(self.sectionlist): 
                    # Initialize storage for ft data
                    ft_titles=[]
                    ft_Subtitles=[]
                    ft_dates =[]
                    ft_titles_finBERTLabel =[]
                    ft_titles_finBERTScore =[]
                    ft_Subtitles_finBERTLabel =[]
                    ft_Subtitles_finBERTScore =[]
                    #vars()[section+'_Group'].append(section)
                    print(f'------------------------------------------{section} started')
                    for pages in tqdm(range(1,self.page_range)):
                        url="https://www.ft.com/{sections}?page={page}".format(page = pages, sections = section)
                        #print(f'------------------------------------------{url}')
                        #url="https://www.ft.com/world?page=2".format(page = pages, sections = section)
                        headers = {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                                    "Accept-Language": "en-US,en;q=0.9",
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                    "Referer": "https://www.ft.com/",
                                    "Connection": "keep-alive",
                                    "Cache-Control": "max-age=0",
                                    }
                        for attempt in range(3):
                            result = requests.get(url, headers=headers)
                            if result.status_code == 200:
                                print("Successful request! Exiting loop.")
                                break
                            print("----------REQUEST CODE : ", result.status_code, url)
                            if attempt < 2:
                                time.sleep(10)
                        
                        reshult=result.content

                        soup=BeautifulSoup(reshult, "lxml")

                        soup = soup.find("div", {'class': 'js-track-scroll-event'})

                        print("LOOKING AT PAGE ",pages)
                        if soup == None: 
                            print("NO SOUP")
                            continue
                        else:
                                
                            for Card in soup.findAll("li",{"class":"o-teaser-collection__item o-grid-row"}):
                                title = Card.find("div", {"class": "o-teaser__heading"})
                                if title == None:
                                    ft_titles.append('none')
                                    ft_titles_finBERTLabel.append(0)
                                    ft_titles_finBERTScore.append(0)
                                else:
                                    titles=title.text
                                    ft_titles.append(titles)
                                    ft_titles = [str(di) if di is None else di for di in ft_titles]
                                    ft_titles_finBERTresults = nlp(titles)
                                    for items in ft_titles_finBERTresults:
                                        ft_titles_finBERTLabel.append(items['label'])
                                        ft_titles_finBERTScore.append(items['score'])

                                Subtitle=Card.find("a",{"class":"js-teaser-standfirst-link"})
                                if Subtitle == None:
                                    ft_Subtitles.append('none')
                                    ft_Subtitles_finBERTLabel.append(0)
                                    ft_Subtitles_finBERTScore.append(0)
                                else:
                                    titles=Subtitle.text
                                    ft_Subtitles.append(titles)
                                    ft_Subtitles = [str(di) if di is None else di for di in ft_Subtitles]
                                    World_Subtitles_finBERTresults = nlp(titles)
                                    for items in World_Subtitles_finBERTresults:
                                        ft_Subtitles_finBERTLabel.append(items['label'])
                                        ft_Subtitles_finBERTScore.append(items['score'])

                                Date=Card.find("time",{"class":"o-date"})
                                if Date == None:
                                    ft_dates.append('none')
                                else:
                                    Dates=Date.get('datetime')
                                    ft_dates.append(Dates)

                    df = pd.DataFrame({'Date': ft_dates, 
                                    'FT_Titles': ft_titles, 
                                    'FT_Subtitles': ft_Subtitles, 
                                    'titles_finBERTLabel': ft_titles_finBERTLabel, 
                                    'titles_finBERTScore': ft_titles_finBERTScore, 
                                    'subtitles_finBERTScore': ft_Subtitles_finBERTScore, 
                                    'subtitles_finBERTLabel':ft_Subtitles_finBERTLabel
                                    })
                    print(df)
                    print("-------------------------3")   
                    df.to_csv(f'{ self.market_data}/{section}.csv', index=False)
                    print(f'{section} saved')
            except Exception as e:
                print(f"Error : {e}")

    def comb_sections(self):
        try:
            combined_data =[]
            cols = ['DATE','TITLE','SUBTITILE','SECTION']
            for section in self.sectionlist:
                df = pd.read_csv(f'{self.output_path}/market/ft/{section}.csv')
                if df.empty:
                    continue
                else:
                    df1 = df.drop(['titles_finBERTLabel','titles_finBERTScore','subtitles_finBERTLabel',    'subtitles_finBERTScore'],axis=1)
                    df1['SECTION'] = section
                    df1.columns = cols
                    combined_data.append(df1)

            if len(combined_data) == 1:
                combined_df = combined_data[0]  # No need to concatenate
            else:
                combined_df = pd.concat(combined_data, ignore_index=True)

            print(combined_df.shape)
            
            combined_df.to_csv(f'{self.allmarketInput}/all_articles_{self.calc_date}.csv', index=False)
            return combined_df
        except Exception as e:
            print(f"Error : {e}")


    