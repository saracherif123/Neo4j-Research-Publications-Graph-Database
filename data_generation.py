import argparse
import os
from tkinter.ttk import Label
import requests
import time
import csv
import random

# Assign path for downloaded data.
os.makedirs('data', exist_ok=True)
OUTPUT_CSV_PATH = os.path.join('data', 'papers.csv')


def main():
    dwnld_conferences(2000)
    dwnld_papers(2000)


# Performs the download and processing of journal articles
def dwnld_papers(n_papers):
    # Obtain a list of journal papers to look up in the following part
    papers = get_papers("JournalArticle")
    paper_ids = [paper['paperId'] for paper in papers]

    n_paper = 1
    for paper_id in paper_ids:
        if n_paper < n_papers:
            paper = get_paper(paper_id)
            try:
                process_paper(paper, n_paper)
            except:
                pass
            n_paper+=1

            # Process the references cited in the paper. A random number is chosen for max references for two reasons:
            # 1. Avoid spending too much time processing references
            # 2. Mantain variability between papers for the graph model.
            max_refs = random.randint(1, 14)
            refs = 0
            for reference in paper['citations']:
                if refs <= max_refs:
                    print(reference)
                    ref_id = reference["paperId"]
                    paper = get_paper(ref_id)
                    refs += 1

                    # Attempt to process the cited paper, if it encounters a problem it skips it
                    try:
                        process_paper(paper, n_paper)
                    except:
                        pass
                else:
                    break
        else:
            break

    # dwnld_conferences()


# Performs the download and processing of conference papers
def dwnld_conferences(n_conferences):
    # Obtain a list of conference papers to look up in the following part
    conferences = get_papers("Conference")
    conference_ids = [conference['paperId'] for conference in conferences]

    # For each conference paper obtain the relevant data
    n_conference = 0
    for conf_id in conference_ids:
        if n_conference < n_conferences:
            # Obtains a paper and attempts to process it into the csv
            paper = get_paper(conf_id)
            try:
                process_paper(paper, n_conference)
            except:
                pass
            n_conference += 1

            # Process the references cited in the paper. A random number is chosen for max references for two reasons:
            # 1. Avoid spending too much time processing references
            # 2. Mantain variability between papers for the graph model.
            max_refs = random.randint(1, 14)
            refs = 0
            for reference in paper['citations']:
                if refs <= max_refs:
                    print(reference)
                    ref_id = reference["paperId"]
                    paper = get_paper(ref_id)
                    refs+=1

                    # Attempt to process the cited paper, if it encounters a problem it skips it
                    try:
                        process_paper(paper, n_conference)
                    except:
                        pass
                else:
                    break
        else:
            break


# Performs a bulk search to obtain the IDs of relevant papers or conferences for further processing
def get_papers(paper_types):
    x = 1
    while x == 1:
        rsp = requests.get(f'https://api.semanticscholar.org/graph/v1/paper/search/bulk',
                           params={'query': "machine | learning",
                                   'publicationTypes': paper_types,
                                   'fieldsOfStudy': "Computer Science,Engineering,Mathematics",
                                   'fields': "paperId",
                                   'minCitationCount': 5})
        try:
            rsp.raise_for_status()
            x = 2
        except:
            time.sleep(1)
    data = rsp.json()
    data = data['data']
    return data


# Performs a search for a particular paper given its ID
def get_paper(paper_id):
    x = 1
    while x == 1:
        rsp = requests.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}',
                           params={'fields': 'paperId,title,year,authors,externalIds,venue,publicationVenue,citations,'
                                             'fieldsOfStudy,publicationTypes,journal,abstract'})
        try:
            rsp.raise_for_status()
            x = 2
        except:
            time.sleep(1)
    return rsp.json()


# Obtain relevant data points from the JSON file provided by the API and process them into a useful csv file
def process_paper(paper, n_run):
    # Select type of operation to perform based on wether it's the first load of the document or not
    operation = 'w' if n_run == 0 else 'a'

    with open(OUTPUT_CSV_PATH, operation, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['PaperId', 'Title', 'Year', 'DOI', 'AuthorId', 'Author', "Main_Author", 'Venue',
                      'VenueID', 'Type', 'FieldOfStudy', 'Volume', 'ReferenceId', 'Reference Name', 'Abstract']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only when it's the first time opening the document
        if operation == 'w':
            writer.writeheader()

        n_author = 0
        for author in paper['authors']:
            for reference in paper["citations"]:
                journal = paper.get('journal', {})
                volume = journal.get('volume', [])
                writer.writerow({
                    "PaperId": paper["paperId"],
                    "Title": paper["title"],
                    "Year": paper["year"],
                    "DOI": paper["externalIds"]["DOI"],
                    "AuthorId": author["authorId"],
                    "Author": author["name"],
                    "Main_Author": 1 if n_author == 0 else 0,
                    "Venue": paper["venue"],
                    "VenueID": paper["publicationVenue"]["id"],
                    "Type": paper["publicationVenue"]["type"],
                    "FieldOfStudy": paper["fieldsOfStudy"][0] if paper["fieldsOfStudy"][0] is not None else "<no_fieldOfStudy_data>",
                    "Volume": volume if volume else "<no_volume_data>",
                    "ReferenceId": reference["paperId"],
                    "Reference Name": reference["title"],
                    "Abstract": paper["abstract"],
                })
            n_author += 1
    csvfile.close()


if __name__ == '__main__':
    main()