import pandas as pd
import ast
import os
import random

# === Configuration ===
DATA_DIR = 'data'
df = pd.read_csv(os.path.join(DATA_DIR, "papers.csv"))

# === Normalize Type and Detect Workshops ===
df['Type'] = df['Type'].fillna('other').str.strip().str.lower()
df.loc[df['Venue'].str.contains("Workshop", case=False, na=False), 'Type'] = 'workshop'

# === Safe FieldOfStudy Parsing ===
def safe_literal_eval(val):
    if isinstance(val, str) and val.strip().startswith("[") and val.strip().endswith("]"):
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
    elif isinstance(val, str) and val.strip() != "":
        return [val.strip()]
    else:
        return []

df['FieldOfStudy'] = df['FieldOfStudy'].apply(safe_literal_eval)

# === Clean Volume Column ===
df['Volume'] = df['Volume'].replace('<no_volume_data>', None)

# === NODES ===

# Paper nodes
papers_df = df[['PaperId', 'Title', 'Year', 'Abstract', 'DOI']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID'
})
papers_df.to_csv(os.path.join(DATA_DIR, "nodes_papers.csv"), index=False)

# Author nodes with synthetic affiliations
authors_df = df[['AuthorId', 'Author']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'Author': 'Name'
})
affiliations = [
    "Massachusetts Institute of Technology", "Stanford University", "University of Oxford",
    "University of Cambridge", "Harvard University", "ETH Zurich",
    "Carnegie Mellon University", "University of Tokyo", "Tsinghua University", "University of Toronto"
]
authors_df['Affiliation'] = [random.choice(affiliations) for _ in range(len(authors_df))]
authors_df.to_csv(os.path.join(DATA_DIR, "nodes_authors.csv"), index=False)

# Keywords nodes
keywords_df = df.explode('FieldOfStudy')[['FieldOfStudy']].drop_duplicates().rename(columns={
    'FieldOfStudy': 'Keyword'
})
keywords_df = keywords_df[keywords_df['Keyword'].notna() & (keywords_df['Keyword'] != '')]
keywords_df['KeywordID'] = keywords_df['Keyword'].factorize()[0].astype(str)
keywords_df = keywords_df[['KeywordID', 'Keyword']]
keywords_df.to_csv(os.path.join(DATA_DIR, "nodes_keywords.csv"), index=False)

# Conference nodes
conference_df = df[df['Type'] == 'conference'][['Venue', 'Year']].drop_duplicates()
conference_df['ConferenceID'] = conference_df['Venue'].factorize()[0].astype(str)
conference_df = conference_df[['ConferenceID', 'Venue', 'Year']]
conference_df.to_csv(os.path.join(DATA_DIR, "nodes_conference.csv"), index=False)

# Journal nodes
journal_df = df[df['Type'] == 'journal'][['Venue', 'Year', 'Volume']].drop_duplicates()
journal_df['JournalID'] = journal_df['Venue'].factorize()[0].astype(str)
journal_df['Volume'] = pd.to_numeric(journal_df['Volume'], errors='coerce').fillna(0).astype(int)
journal_df = journal_df[['JournalID', 'Venue', 'Year', 'Volume']]
journal_df.to_csv(os.path.join(DATA_DIR, "nodes_journal.csv"), index=False)

# Workshop nodes
workshop_df = df[df['Type'] == 'workshop'][['Venue', 'Year']].drop_duplicates()
workshop_df['WorkshopID'] = workshop_df['Venue'].factorize()[0].astype(str)
workshop_df = workshop_df[['WorkshopID', 'Venue', 'Year']]
workshop_df.to_csv(os.path.join(DATA_DIR, "nodes_workshop.csv"), index=False)

# === RELATIONSHIPS ===

# AUTHOR_OF
author_of_df = df[['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'PaperId': 'PaperID'
})
author_of_df.to_csv(os.path.join(DATA_DIR, "rel_author_of.csv"), index=False)

# CORRESPONDING_AUTHOR
corresponding_author_df = df[df['Main_Author'] == 1][['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
    'AuthorId': 'AuthorID',
    'PaperId': 'PaperID'
})
corresponding_author_df.to_csv(os.path.join(DATA_DIR, "rel_corresponding_author.csv"), index=False)

# ABOUT (Paper -> Keyword)
keywords_map = dict(zip(keywords_df['Keyword'], keywords_df['KeywordID']))
about_df = df.explode('FieldOfStudy')[['PaperId', 'FieldOfStudy']].drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'FieldOfStudy': 'Keyword'
})
about_df['KeywordID'] = about_df['Keyword'].map(keywords_map)
about_df = about_df[['PaperID', 'KeywordID']]
about_df.to_csv(os.path.join(DATA_DIR, "rel_about.csv"), index=False)

# RELATED (Paper -> Paper)
related_df = df[['PaperId', 'ReferenceId']].dropna().drop_duplicates().rename(columns={
    'PaperId': 'PaperID',
    'ReferenceId': 'RelatedToPaperID'
})
related_df.to_csv(os.path.join(DATA_DIR, "rel_related.csv"), index=False)

# === PUBLISHED_IN relationships using Venue + Year ===

# Conference
published_in_conference_df = (
    df[df['Type'] == 'conference'][['PaperId', 'Venue', 'Year']]
    .merge(conference_df[['ConferenceID', 'Venue', 'Year']], on=['Venue', 'Year'])
    [['PaperId', 'ConferenceID']]
    .drop_duplicates()
    .rename(columns={'PaperId': 'PaperID'})
)
published_in_conference_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_conference.csv"), index=False)

# Journal
published_in_journal_df = (
    df[df['Type'] == 'journal'][['PaperId', 'Venue', 'Year']]
    .merge(journal_df[['JournalID', 'Venue', 'Year']], on=['Venue', 'Year'])
    [['PaperId', 'JournalID']]
    .drop_duplicates()
    .rename(columns={'PaperId': 'PaperID'})
)
published_in_journal_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_journal.csv"), index=False)

# Workshop
published_in_workshop_df = (
    df[df['Type'] == 'workshop'][['PaperId', 'Venue', 'Year']]
    .merge(workshop_df[['WorkshopID', 'Venue', 'Year']], on=['Venue', 'Year'])
    [['PaperId', 'WorkshopID']]
    .drop_duplicates()
    .rename(columns={'PaperId': 'PaperID'})
)
published_in_workshop_df.to_csv(os.path.join(DATA_DIR, "rel_published_in_workshop.csv"), index=False)

# === REVIEWS (Synthetic) ===
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
