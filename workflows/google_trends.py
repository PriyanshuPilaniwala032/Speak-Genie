import json
import time
import pandas as pd
import random
import requests
import urllib3
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_google_trends_data(keywords, countries=['US', 'IN']):
    """
    Fetches Google Trends data for a list of keywords across specified countries.
    """
    all_trends_data = []
    print("Initializing Google Trends collector...")
    time.sleep(5)
    for country in countries:
        print(f"  -> Processing Google Trends for Country: {country}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), requests_args={'headers': headers, 'verify':False})

        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]
            print(f"    -> Fetching batched interest for {batch} in {country}...")
            pytrends.build_payload(batch, cat=0, timeframe='today 3-m', geo=country)
            interest_df = pytrends.interest_over_time()
            
            if not interest_df.empty and 'isPartial' not in interest_df.columns:
                 for kw in batch:
                    if kw in interest_df.columns:
                        avg_interest = round(interest_df[kw].mean(), 2)
                        all_trends_data.append({
                            "workflow": kw,
                            "platform": "Google Trends",
                            "link": f"https://trends.google.com/trends/explore?q={kw.replace(' ', '%20')}&geo={country}",
                            "popularity_metrics": {"average_search_interest": avg_interest},
                            "country": country
                        })
            time.sleep(random.randint(15, 25))

    return all_trends_data

