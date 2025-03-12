# Import the necessary libraries
import requests
import json

#Fill out the information for the API request
query = "graph | data" #Names that show up in the paper title (Either learning or machine)
fields = "title,year,authors,venue,fieldsOfStudy,publicationTypes,journal,abstract" #Fields you wish to get
publicationTypes = "JournalArticle,Conference"
fieldsOfStudy = "Computer Science"

# I looked into the API documentation for Bulk Search that you can find here:
# https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_paper_bulk_search
url = f"http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&publicationTypes={publicationTypes}&year=2025-&fieldsOfStudy={fieldsOfStudy}"
r = requests.get(url).json()

#All of this is from the example here:
# https://github.com/allenai/s2-folks/blob/main/examples/python/search_bulk/get_dataset.py
print(f"Will retrieve an estimated {r['total']} documents")
retrieved = 0

with open(f"papers.jsonl", "a") as file:
    while True:
        if "data" in r:
            retrieved += len(r["data"])
            print(f"Retrieved {retrieved} papers...")
            for paper in r["data"]:
                print(json.dumps(paper), file=file)
        if "token" not in r:
            break
        r = requests.get(f"{url}&token={r['token']}").json()

print(f"Done! Retrieved {retrieved} papers total")