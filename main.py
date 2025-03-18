import argparse
import os
import requests
import time
import csv

# Obtains a paper given an id number and writes it into a csv file.
def main():
    # id = "5c5751d45e298cea054f32b392c12c61027d2fe7"
    id = "913f54b44dfb9202955fe296cf5586e1105565ea"
    paper = get_paper(id)

    # Assign a type to the paper obtained
    types = paper.get("publicationTypes", [])
    if "Conference" in types:
        paper_type = "Conference"
    elif "JournalArticle" in types:
        paper_type = "Journal"
    else:
        paper_type = "Other"

    #Write into CSV file
    with open('papers.csv', 'w') as csvfile:
        fieldnames = ['PaperId', 'Title', 'Year', 'AuthorId', 'Author', "Main_Author", 'Venue', 'Type', 'FieldOfStudy', 'PublicationType', 'Volume', 'ReferenceId', 'Reference Name', 'Abstract']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        n = 0
        for author in paper['authors']:
            for reference in paper["references"]:
                journal = paper.get('journal', [])
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
                    'PublicationType': paper["publicationTypes"][0],
                    'Volume': volume if volume else '<no_volume_data>',
                    'ReferenceId': reference["paperId"],
                    'Reference Name': reference["title"],
                    'Abstract': paper['abstract'],
                })
            n+= 1
    csvfile.close()

    # Find related papers and get their info
    references = paper.get('references', [])

    references = get_references(references)
    m=0
    while m < 10:
        print(f"Run number: {m}")
        for reference in references:
            print(reference)
            try:
                references = get_references(reference)
            except:
                pass
        m+=1

# Requests information about a paper given an ID. Returns a JSON file with paper info
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

            # Obtain the references of the paper for future processing
            references = paper.get('references', [])
            refs.append(references)

            try:
                if "Conference" in types:
                    paper_type = "Conference"
                elif "JournalArticle" in types:
                    paper_type = "Journal"
                else:
                    paper_type = "Other"
            except:
                paper_type = "Other"

            # Write into CSV file
            with open('papers.csv', 'a') as csvfile:
                fieldnames = ['PaperId', 'Title', 'Year', 'AuthorId', 'Author', "Main_Author", 'Venue', 'Type',
                              'FieldOfStudy', 'PublicationType', 'Volume', 'ReferenceId', 'Reference Name',
                              'Abstract']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                n = 0
                for author in paper['authors']:
                    for reference in paper["references"]:
                        journal = paper.get('journal', [])
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
                            'PublicationType': paper["publicationTypes"][0],
                            'Volume': volume if volume else '<no_volume_data>',
                            'ReferenceId': reference["paperId"],
                            'Reference Name': reference["title"],
                            'Abstract': paper['abstract'],
                        })
                    n += 1
                last_paper = paper
            csvfile.close()
        else:
            print("No reference")

    # Return the references of the last paper obtained
    return refs

if __name__ == '__main__':
    main()