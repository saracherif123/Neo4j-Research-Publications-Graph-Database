import pandas as pd
import ast
import os
import random

# Define the data folder path
DATA_DIR = 'data'

# Load the CSV file
df = pd.read_csv(os.path.join(DATA_DIR, "papers.csv"))

# === Fix missing or incorrect type ===
df['Type'] = df['Type'].fillna('other').str.lower()

# === NODES ===

# Paper nodes
papers_df = df[['PaperId', 'Title', 'Year', 'Abstract']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID'
})
papers_df['DOI'] = None
papers_df.to_csv(os.path.join(DATA_DIR, "nodes_papers.csv"), index=False)

# Author nodes with synthetic affiliations
authors_df = df[['AuthorId', 'Author']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'Author': 'Name'
})

# Generate synthetic affiliations
affiliations = [
    "Massachusetts Institute of Technology",
    "Stanford University",
    "University of Oxford",
    "University of Cambridge",
    "Harvard University",
    "ETH Zurich",
    "Carnegie Mellon University",
    "University of Tokyo",
    "Tsinghua University",
    "University of Toronto"
]
authors_df['Affiliation'] = [random.choice(affiliations) for _ in range(len(authors_df))]
authors_df.to_csv(os.path.join(DATA_DIR, "nodes_authors.csv"), index=False)

# Keywords node
df['FieldOfStudy'] = df['FieldOfStudy'].apply(ast.literal_eval)
keywords_df = df.explode('FieldOfStudy')[['FieldOfStudy']].drop_duplicates().rename(columns={
    'FieldOfStudy': 'Keyword'
})
keywords_df['KeywordID'] = keywords_df['Keyword'].factorize()[0].astype(str)
keywords_df.to_csv(os.path.join(DATA_DIR, "nodes_keywords.csv"), index=False)

# Conference nodes
conference_df = df[df['Type'] == 'conference'][['Venue', 'Year']].drop_duplicates().rename(columns={
    'Venue': 'Name'
})
conference_df['Venue'] = conference_df['Name']
conference_df.to_csv(os.path.join(DATA_DIR, "nodes_conference.csv"), index=False)

# Journal nodes
journal_df = df[df['Type'] == 'journal'][['Venue', 'Year']].drop_duplicates().rename(columns={
    'Venue': 'Name'
})
journal_df['ISBN'] = None
journal_df['Volume'] = None
journal_df.to_csv(os.path.join(DATA_DIR, "nodes_journal.csv"), index=False)

# Workshop nodes
workshop_df = df[df['Type'] == 'workshop'][['Venue', 'Year']].drop_duplicates().rename(columns={
    'Venue': 'Name'
})
workshop_df['Venue'] = workshop_df['Name']
workshop_df.to_csv(os.path.join(DATA_DIR, "nodes_workshop.csv"), index=False)

# === RELATIONSHIPS ===

# AUTHOR_OF relationship
author_of_df = df[['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'PaperId': 'PaperID'
})
author_of_df.to_csv(os.path.join(DATA_DIR, "rel_author_of.csv"), index=False)

# CORRESPONDING_AUTHOR relationship
corresponding_author_df = df[df['Main_Author'] == 1][['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'PaperId': 'PaperID'
})
corresponding_author_df.to_csv(os.path.join(DATA_DIR, "rel_corresponding_author.csv"), index=False)

# ABOUT relationship (Paper -> Keywords)
keywords_map = dict(zip(keywords_df['Keyword'], keywords_df['KeywordID']))
about_df = df.explode('FieldOfStudy')[['PaperId', 'FieldOfStudy']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'FieldOfStudy': 'Keyword'
})
about_df['KeywordID'] = about_df['Keyword'].map(keywords_map)
about_df = about_df[['PaperID', 'KeywordID']]
about_df.to_csv(os.path.join(DATA_DIR, "rel_about.csv"), index=False)

# RELATED relationship (Paper -> Paper)
related_df = df[['PaperId', 'ReferenceId']].dropna().drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'ReferenceId': 'RelatedToPaperID'
})
related_df.to_csv(os.path.join(DATA_DIR, "rel_related.csv"), index=False)

# PUBLISHED_IN relationships
published_in_conference_df = df[df['Type'] == 'conference'][['PaperId', 'Venue']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'Venue': 'ConferenceID'
})
published_in_conference_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_conference.csv"), index=False)

published_in_journal_df = df[df['Type'] == 'journal'][['PaperId', 'Venue']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'Venue': 'JournalID'
})
published_in_journal_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_journal.csv"), index=False)

published_in_workshop_df = df[df['Type'] == 'workshop'][['PaperId', 'Venue']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'Venue': 'WorkshopID'
})
published_in_workshop_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_workshop.csv"), index=False)

# === REVIEWS relationship ===

def generate_comment():
    comments = [
        "Excellent contribution to the field.",
        "Needs more empirical validation.",
        "Well-structured and informative.",
        "Interesting methodology.",
        "Limited novelty but useful results."
    ]
    return random.choice(comments)

review_df = df[['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
    'AuthorId': 'ReviewerID',
    'PaperId': 'PaperID'
})
review_df['Comment'] = [generate_comment() for _ in range(len(review_df))]
review_df['Score'] = [random.randint(1, 5) for _ in range(len(review_df))]
review_df.to_csv(os.path.join(DATA_DIR, "rel_reviews.csv"), index=False)
