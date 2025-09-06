import json
import requests
import pandas as pd
import dotenv
import os

dotenv.load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def fetch_github_data(search_query="n8n workflow", limit=50):
    """
    Searches GitHub for top repositories matching a query, sorted by stars.

    Args:
        search_query (str): The search term.
        limit (int): The max number of repositories to return.

    Returns:
        list: A list of dictionaries with repository data.
    """
    print("Searching GitHub for top repositories...")
    

    url = f"https://api.github.com/search/repositories"
    
    # Parameters for the search
    params = {
        'q': search_query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': limit
    }
    
    # Headers for authentication
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN and GITHUB_TOKEN != 'YOUR_GITHUB_PERSONAL_ACCESS_TOKEN_HERE':
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    else:
        print("Warning: No GitHub token provided. Making unauthenticated request (lower rate limit).")

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        collected_repos = []
        
        for repo in data.get('items', []):
            repo_details = {
                "workflow": repo['full_name'], 
                "platform": "GitHub",
                "link": repo['html_url'],
                "popularity_metrics": {
                    "stars": repo['stargazers_count'],
                    "forks": repo['forks_count'],
                    "watchers": repo['watchers_count']
                },
                "country": "N/A"
            }
            collected_repos.append(repo_details)
            
        return collected_repos

    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred: {e}")
        if e.response.status_code == 401:
            print("  -> This is likely due to an invalid GitHub token.")
        elif e.response.status_code == 403:
            print("  -> This is likely due to hitting the API rate limit.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return []

# if __name__ == "__main__":
#     github_data = fetch_github_data()
    
#     if github_data:
#         df = pd.DataFrame(github_data)
#         print("\n--- Collected GitHub Workflows ---")
#         print(df)
#         print("----------------------------------\n")

#         output_filename = 'github_data.json'
#         with open(output_filename, 'w', encoding='utf-8') as f:
#             json.dump(github_data, f, indent=4, ensure_ascii=False)
#         print(f"Successfully saved {len(github_data)} repositories to {output_filename}")