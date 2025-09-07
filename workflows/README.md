# n8n Workflow Popularity System

A fully automated system that identifies, ranks, and serves the most popular n8n workflows from GitHub, YouTube, and the n8n Community Forum via a REST API and interactive frontend dashboard.

## Installation and Set-Up

#### Clone the repository 

```git clone https://github.com/PriyanshuPilaniwala032/Speak-Genie.git```
```cd ./Speak-Genie/workflows```


#### Install the requiremens using the following command:

```pip install -r requirements.txt```

#### Confirgure API keys

Make ```.env``` and configure your API keys
```YOUTUBE_API_KEY="your_api_key_here"``` 
```GITHUB_TOKEN="your_api_key_here"``` 

## Running the System

Run the main pipeline by 

```python main.py```

After this start the API server

```uvicorn api:app --reload```

To view the frontend open the ```index.html``` file in your web browser to see the web app in action. The dashboard will automatically connect to your running API.

## API Endpoints

```GET /```: Retrieves the complete, ranked list of popular workflows. This is the primary data endpoint.

```POST /refresh```: Triggers the main.py data collection script to run as a background process, allowing for on-demand data updates.

You can view interactive API documentation by running the server and visiting ```http://127.0.0.1:8000/docs.```
