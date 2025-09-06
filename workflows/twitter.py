import os
import json
import requests
import pandas as pd

# --- IMPORTANT: FILL THIS IN AS AN ENVIRONMENT VARIABLE ---
# You get this from your Twitter/X Developer Portal
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAAPX03wEAAAAAc7AjrNTKGH%2FGkPD3P72Apj9zpOk%3DmEpYFGhT2LTD5RSq8Acp6UEwTQvjlMPlZa7GTGc8oRytRM7kIj')

def fetch_twitter_data(search_queries, limit=50):
    """
    Searches Twitter for recent, popular tweets matching a query.
    """
    print("Searching Twitter for popular tweets...")
    
    if 'YOUR_BEARER_TOKEN_HERE' in BEARER_TOKEN:
        print("ERROR: Please provide your Twitter Bearer Token in the script for this test.")
        return []

    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    
    collected_tweets = []

    for query in search_queries:
        print(f"  -> Searching for: '{query}'")
        # -is:retweet ensures we get original posts
        params = {
            'query': f'"{query}" -is:retweet',
            'max_results': limit if limit <= 100 else 100, # API max is 100 per request
            'tweet.fields': 'public_metrics,created_at',
            'expansions': 'author_id',
            'user.fields': 'username'
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            json_response = response.json()
            
            tweets = json_response.get('data', [])
            users = {user['id']: user for user in json_response.get('includes', {}).get('users', [])}

            for tweet in tweets:
                author_info = users.get(tweet['author_id'], {})
                metrics = tweet.get('public_metrics', {})
                tweet_details = {
                    "workflow": tweet['text'],
                    "platform": "Twitter",
                    "link": f"https://twitter.com/{author_info.get('username', 'anyuser')}/status/{tweet['id']}",
                    "popularity_metrics": {
                        "retweets": metrics.get('retweet_count', 0),
                        "likes": metrics.get('like_count', 0),
                        "replies": metrics.get('reply_count', 0)
                    },
                    "country": "N/A", # Twitter data is not country-specific
                    "metadata": { # Extra enriched metadata
                        "author": author_info.get('username', 'N/A'),
                        "published_at": tweet.get('created_at')
                    }
                }
                collected_tweets.append(tweet_details)
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while calling the Twitter API: {e}")
            # Don't stop the whole pipeline if one source fails
            continue
            
    return collected_tweets

# --- NEW: Added this block to make the script runnable ---
if __name__ == "__main__":
    # For a quick test, you can paste your Bearer Token here.
    # For production (like on Render), it's better to use environment variables.
    if 'YOUR_BEARER_TOKEN_HERE' in BEARER_TOKEN:
        # To test, replace the placeholder below with your actual token
        # Example: BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAA..._YOUR_TOKEN_...BBBBBBBBBBBB"
        pass # Keep this as 'pass' if you set an environment variable

    # Define the search terms for the test
    test_queries = ["n8n workflow", "#n8n", "n8n.io automation"]
    
    # Call the main function to fetch data
    twitter_data = fetch_twitter_data(test_queries, limit=25)
    
    if twitter_data:
        # Use pandas for a clean printout to the console
        df = pd.DataFrame(twitter_data)
        print("\n--- Collected Twitter Data ---")
        print(df.head()) # Print the first 5 results
        print("----------------------------\n")

        # Save the results to a JSON file
        output_filename = 'twitter_data.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(twitter_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(twitter_data)} tweets to {output_filename}")

