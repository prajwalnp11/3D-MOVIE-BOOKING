import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")

url = "https://api.themoviedb.org/3/movie/popular"

headers = {
    "accept": "application/json"
}

params = {
    "api_key": api_key,
    "language": "en-US",
    "page": 1
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=20
)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("\nTMDB CONNECTION SUCCESSFUL!")
    print("\nPopular Movies:\n")

    for movie in data["results"][:10]:
        print("Title:", movie["title"])
        print("Rating:", movie["vote_average"])
        print("Release Date:", movie["release_date"])
        print("-------------------------")
else:
    print("API request failed.")
    print(response.text)
