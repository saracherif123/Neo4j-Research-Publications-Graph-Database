import argparse
import os
import requests
import time
import csv

os.makedirs('data', exist_ok=True)
OUTPUT_CSV_PATH = os.path.join('data', 'papers.csv')

# Obtains a paper given an id number and writes it into a csv file.
def main():
    id = "913f54b44dfb9202955fe296cf5586e1105565ea"
    paper = get_paper(id)

    types = paper.get("publicationTypes", [])
    if "Conference" in types:
        paper_type = "Conference"
    elif "JournalArticle" in types:
        paper_type = "Journal"
    else:
        paper_type = "Other"

    with open(OUTPUT_CSV_PATH, 'w') as csvfile:
        fieldnames = ['PaperId', 'Title', 'Year', 'AuthorId', 'Author', "Main_Author", 'Venue', 'Type', 'FieldOfStudy', 'PublicationType', 'Volume', 'ReferenceId', 'Reference Name', 'Abstract']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        n = 0
        for author in paper['authors']:
            for reference in paper["references"]:
                journal = paper.get('journal', {})
                volume = journal.get('volume', [])
                writer.writerow({
                    'PaperId': paper["paperId"],
                    'Title': paper['title'],
                    'Year': paper['year'],
                    'AuthorId': author["authorId"],
                    'Author': author["name"],
                    'Main_Author': 1 if n == 0 else 0,
                    'Venue': paper["venue"],
                    'Type': paper_type,
                    'FieldOfStudy': paper["fieldsOfStudy"],
                    'PublicationType': paper.get("publicationTypes", ['<unknown>'])[0],
                    'Volume': volume if volume else '<no_volume_data>',
                    'ReferenceId': reference["paperId"],
                    'Reference Name': reference["title"],
                    'Abstract': paper['abstract'],
                })
            n += 1

    references = paper.get('references', [])
    references = get_references(references)
    m = 0
    while m < 10:
        print(f"Run number: {m}")
        for reference in references:
            print(reference)
            try:
                references = get_references(reference)
            except:
                pass
        m += 1

def get_paper(paper_id):
    x = 1
    while x == 1:
        rsp = requests.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}',
                           params={'fields': 'paperId,title,year,authors,venue,publicationVenue,references,fieldsOfStudy,publicationTypes,journal,abstract'})
        try:
            rsp.raise_for_status()
            x = 2
        except:
            time.sleep(1)
    return rsp.json()

def get_references(references):
    refs = []
    for reference in references:
        if reference["paperId"]:
            print(reference)
            id = reference["paperId"]
            paper = get_paper(id)

            types = paper.get("publicationTypes", [])

            references = paper.get('references', [])
            refs.append(references)

            if "Conference" in types:
                paper_type = "Conference"
            elif "JournalArticle" in types:
                paper_type = "Journal"
            else:
                paper_type = "Other"

            with open(OUTPUT_CSV_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['PaperId', 'Title', 'Year', 'AuthorId', 'Author', "Main_Author", 'Venue', 'Type',
                              'FieldOfStudy', 'PublicationType', 'Volume', 'ReferenceId', 'Reference Name',
                              'Abstract']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                n = 0
                for author in paper['authors']:
                    for reference in paper["references"]:
                        journal = paper.get('journal', {})
                        volume = journal.get('volume', [])
                        writer.writerow({
                            'PaperId': paper["paperId"],
                            'Title': paper['title'],
                            'Year': paper['year'],
                            'AuthorId': author["authorId"],
                            'Author': author["name"],
                            'Main_Author': 1 if n == 0 else 0,
                            'Venue': paper["venue"],
                            'Type': paper_type,
                            'FieldOfStudy': paper["fieldsOfStudy"],
                            'PublicationType': paper.get("publicationTypes", ['<unknown>'])[0],
                            'Volume': volume if volume else '<no_volume_data>',
                            'ReferenceId': reference["paperId"],
                            'Reference Name': reference["title"],
                            'Abstract': paper['abstract'],
                        })
                    n += 1
        else:
            print("No reference")

    return refs

if __name__ == '__main__':
    main()
