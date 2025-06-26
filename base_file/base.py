import pandas as pd
import os
from openai import OpenAI

class Properties:
    client = OpenAI(api_key="")

    #today = datetime.datetime.today()
    #today = pd.to_datetime("2024-12-01")
    calc_date1 = pd.to_datetime("2025-02-17")
    calc_date = calc_date1.strftime("%Y-%m-%d")
    #startdate = calc_date - pd.DateOffset(months=12)
    startdate1 = pd.to_datetime("2024-08-05")
    startdate = startdate1.strftime("%Y-%m-%d")
    pagestockRange = 15
    pageRange = 30
    sectionList =[
                'world',
                'global-economy',
                'world-uk']
                # 'us',
                # 'uk-business-economy']
                # 'uk-politics-policy', 
                # 'uk-companies', 
                # 'us-economy',
                # 'us-companies',
                # 'us-politics-policy'
                # 'equities', #Can change for specific asset class in the future 
                # 'us-equities',
                # 'technology-sector']#Can change for specific sectors class in the future

    
    
    outputMode = "Output_prod"
    outputPath = f"{outputMode}/{calc_date}/"
    allstockOutput = f"{outputPath}/search"
    stockInput = f"{outputPath}/search/FinBert" 
    stockOutput = f"{outputPath}/search/GPT"
    stockOutput1 = f"{outputPath}/search/combined_scores"
    allmarketInput = f"{outputPath}/market"
    marketInput = f"{allmarketInput}/ft"
    marketOutput = f"{allmarketInput}/GPT"
    marketOutput1 = f"{allmarketInput}/combined_scores"
    rfReturns = "10_year_return_rate.csv"
    marketPortfolio = "Emotionalmarket/marketportfolio.csv"
    stockPortfolio = "Emotionalmarket/TSLA.csv"
    targetPath = "Emotionalmarket/Targets_NASDAQ.csv"
    stockName = "Tesla, Inc. "
    stockTicker = "TSLA"

    #replacing column names
    stock_old_cols = ['Date','COMPANY','Tesla, Inc. _FT_Titles','titles_finBERTLabel','titles_finBERTScore',
            'Tesla, Inc. _FT_Titles_GPT_SENTIMENT','Tesla, Inc. _FT_Titles_GPT_SCORE',
            'Tesla, Inc. _FT_Subtitles','Subtitles_finBERTLabel','Subtitles_finBERTScore',
            'Tesla, Inc. _FT_Subtitles_GPT_SENTIMENT','Tesla, Inc. _FT_Subtitles_GPT_SCORE']
    
    market_old_cols = ['dates','SECTION', 'FT_Titles', 
                  'titles_finBERTLabel','titles_finBERTScore', 'FT_Titles_GPT_SENTIMENT','FT_Titles_GPT_SCORE',
                  'FT_Subtitles','subtitles_finBERTLabel','subtitles_finBERTScore',        'FT_Subtitles_GPT_SENTIMENT','FT_Subtitles_GPT_SCORE']
    
    market_new_cols = ['DATE','MKT_FT_SECTION','MKT_FT_TITLE','MKT_T_FINBERT_SENTIMENT','MKT_T_FINBERT_SCORE','MKT_T_GPT_SENTIMENT' ,
                        'MKT_T_GPT_SCORE','MKT_FT_SUBTITLE','MKT_ST_FINBERT_SENTIMENT','MKT_ST_FINBERT_SCORE','MKT_ST_GPT_SENTIMENT','MKT_ST_GPT_SCORE']
        
    stock_new_cols =['DATE','COMPANY','FT_TITLE','T_FINBERT_SENTIMENT','T_FINBERT_SCORE','T_GPT_SENTIMENT','T_GPT_SCORE',
        'FT_SUBTITLE','ST_FINBERT_SENTIMENT','ST_FINBERT_SCORE','ST_GPT_SENTIMENT','ST_GPT_SCORE']
    
    @staticmethod
    def ensure_directories():
        """Ensure required directories exist"""
        directories = [Properties.outputPath, Properties.marketInput,Properties.stockInput,
                       Properties.marketOutput,Properties.marketOutput1,
                       Properties.stockOutput,Properties.stockOutput1]
        for directory in directories:
            if directory:  # Ensure it's not None or empty
                os.makedirs(directory, exist_ok=True)
                print(f"Directory ensured: {directory}")

Properties.ensure_directories()