import os
import json
import pandas as pd
import numpy as np  

try:
    from forum import fetch_forum_data
    from youtube import fetch_youtube_data
    from github import fetch_github_data
except ImportError as e:
    print(f"Error: Could not import a collector function. Details: {e}")
    exit()


def run_all_collectors():
    """
    Runs all data collectors, including country-specific searches for YouTube.
    """
    print("--- Starting Data Collection Phase ---")
    
    # --- 1. n8n Forum ---
    print("\n[1/3] Collecting from n8n Forum...")
    forum_search_terms = [
        "workflow", "automation", "google sheets", "slack", "api", "webhook",
        "discord", "airtable", "notion", "database", "gmail", "openai", "shopify",
        "telegram", "typeform", "jira", "hubspot", "wordpress", "rss feed", "crm sync"
    ]
    forum_data = []
    for term in forum_search_terms:
        # Fetching a focused number of top results per term ensures quality
        forum_data.extend(fetch_forum_data(term, limit=1150))
    with open('forum_data.json', 'w', encoding='utf-8') as f:
        json.dump(forum_data, f, indent=4, ensure_ascii=False)
    print(f"  -> Saved {len(forum_data)} records to forum_data.json")

    # --- 2. YouTube ---
    print("\n[2/3] Collecting from YouTube with country segmentation...")
    youtube_search_terms = [
        "n8n workflow", "n8n automation", "n8n tutorial", 
        "n8n google sheets", "n8n slack", "n8n airtable",
        "n8n discord notification", "n8n shopify", "n8n vs make",
        "n8n typeform", "n8n self host", "n8n postgres"
    ]
    youtube_data = []
    countries = ['US', 'IN']
    for country_code in countries:
        print(f"  -> Searching YouTube for region: {country_code}")
        for term in youtube_search_terms:
            youtube_data.extend(fetch_youtube_data(term, limit=50, region_code=country_code))

    with open('youtube_data.json', 'w', encoding='utf-8') as f:
        json.dump(youtube_data, f, indent=4, ensure_ascii=False)
    
    print(f"  -> Saved {len(youtube_data)} total records to youtube_data.json")

     # --- 3. GitHub ---
    print("\n[3/3] Collecting from GitHub with expanded queries...")
    github_search_queries = ["n8n workflow", "n8n-nodes", "n8n custom", "n8n self-hosted"]
    github_data = []

    for query in github_search_queries:
        github_data.extend(fetch_github_data(search_query=query, limit=2000))
    
    with open('github_data.json', 'w', encoding='utf-8') as f:
        json.dump(github_data, f, indent=4, ensure_ascii=False)

    print(f"  -> Saved {len(github_data)} records to github_data.json")    
    print("\n--- Data Collection Phase Complete ---")

def calculate_popularity_score(df):
    """
    Calculates a popularity score using logarithmic scaling to better handle outliers.
    """
    print("  -> Calculating popularity scores with logarithmic scaling...")
    df['score'] = 0.0

    def normalize_log_scale(series):
        series = pd.to_numeric(series, errors='coerce').fillna(0)
        log_scaled = np.log1p(series)
        min_val, max_val = log_scaled.min(), log_scaled.max()
        if max_val > min_val:
            return ((log_scaled - min_val) / (max_val - min_val)) * 100
        return pd.Series(0, index=series.index)

    # Forum: based on views
    forum_mask = df['platform'] == 'Forum'
    if not df.loc[forum_mask].empty:
        forum_views = df.loc[forum_mask, 'popularity_metrics'].apply(lambda x: x.get('views', 0))
        df.loc[forum_mask, 'score'] = normalize_log_scale(forum_views)

    # YouTube: based on views
    youtube_mask = df['platform'] == 'YouTube'
    if not df.loc[youtube_mask].empty:
        youtube_views = df.loc[youtube_mask, 'popularity_metrics'].apply(lambda x: x.get('views', 0))
        df.loc[youtube_mask, 'score'] = normalize_log_scale(youtube_views)
        
    # GitHub: based on stars
    github_mask = df['platform'] == 'GitHub'
    if not df.loc[github_mask].empty:
        github_stars = df.loc[github_mask, 'popularity_metrics'].apply(lambda x: x.get('stars', 0))
        df.loc[github_mask, 'score'] = normalize_log_scale(github_stars)
    
    return df

def combine_and_clean_data():
    print("\n--- Starting Data Combination and Cleaning Phase ---")
    data_files = ['forum_data.json', 'youtube_data.json', 'github_data.json']
    all_data = []
    for file_name in data_files:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    all_data.extend(json.load(f))
                print(f"  -> Loaded {len(all_data)} total records so far from {file_name}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"  -> WARNING: Could not read or parse {file_name}. Error: {e}")
    
    if not all_data:
        print("No data was collected. Exiting.")
        return

    df = pd.DataFrame(all_data)
    df['country'] = df['country'].fillna('Global')
    if 'metadata' not in df.columns:
        df['metadata'] = [{} for _ in range(len(df))]
    df['metadata'] = df['metadata'].apply(lambda x: {} if pd.isna(x) else x)
    
    # df.drop_duplicates(subset=['link'], inplace=True, keep='first')
    
    df = calculate_popularity_score(df)
    
    df = df.sort_values(by='score', ascending=False)
    
    final_dataset = df.to_dict('records')
    with open('final_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccessfully combined and cleaned data. Total unique workflows: {len(final_dataset)}")
    print("--- Pipeline Finished ---")

if __name__ == "__main__":
    run_all_collectors()
    combine_and_clean_data()