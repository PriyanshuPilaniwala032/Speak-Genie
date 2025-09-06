import requests
import json
import pandas as pd

def fetch_forum_data(search_term, limit=50):
    """
    Fetches workflow data from the n8n Discourse forum, sorted by popularity (views).

    Args:
        search_term (str): The keyword to search for (e.g., "workflow").
        limit (int): The number of workflows to try and fetch.

    Returns:
        list: A list of dictionaries, where each dictionary is a workflow.
    """
    print(f"Searching n8n forum for most popular: '{search_term}'...")
    
    search_url = "https://community.n8n.io/search.json"
    
    # Sorting by views is a great way to find popular/high-quality topics.
    params = {'q': search_term, 'order': 'views'}
    
    collected_workflows = []

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status() 
        data = response.json()

        topics = data.get('topics', [])
        
        if not topics:
            print("No topics found for the search term.")
            return []

        print(f"Found {len(topics)} topics. Extracting details...")

        for topic in topics:
            if len(collected_workflows) >= limit:
                break
            
            slug = topic.get('slug')
            topic_id = topic.get('id')
            link = f"https://community.n8n.io/t/{slug}/{topic_id}"

            workflow_details = {
                "workflow": topic.get('title'),
                "platform": "Forum",
                "link": link,
                "popularity_metrics": {
                    "views": topic.get('views', 0),
                    "replies": topic.get('reply_count', 0),
                    "likes": topic.get('like_count', 0)
                },
                "country": "N/A" 
            }
            collected_workflows.append(workflow_details)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return [] 
    except KeyError as e:
        print(f"Could not find key {e} in the response JSON. The API structure might have changed.")
        return []

    return collected_workflows

# if __name__ == "__main__":
#     search_terms = ["workflow", "automation", "google sheets", "slack integration", "api", "database", "webhook"]
#     all_workflows = []

#     for term in search_terms:
#         # We'll fetch a smaller number of top results per search term to ensure high quality
#         workflows = fetch_forum_data(term, limit=10)
#         all_workflows.extend(workflows)
#         print(f"Collected {len(workflows)} top workflows for '{term}'.")

#     # Remove potential duplicates if a popular workflow appeared in multiple searches
#     # We'll use the link as a unique identifier
#     unique_workflows = {wf['link']: wf for wf in all_workflows}.values()
#     final_workflows = list(unique_workflows)[:50]

#     # Use pandas for a nice, clean printout to the console
#     df = pd.DataFrame(final_workflows)
#     print("\n--- Collected Forum Workflows ---")
#     print(df)
#     print("---------------------------------\n")

#     # Save the final list to a JSON file
#     output_filename = 'forum_data.json'
#     try:
#         with open(output_filename, 'w', encoding='utf-8') as f:
#             json.dump(final_workflows, f, indent=4, ensure_ascii=False)
#         print(f"Successfully saved {len(final_workflows)} workflows to {output_filename}")
#     except IOError as e:
#         print(f"Error saving data to file: {e}")

