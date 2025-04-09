import pandas as pd
import ast
import os
import random

def main():
    # === Configuration ===
    DATA_DIR = 'data'
    df = pd.read_csv(os.path.join(DATA_DIR, "papers.csv"))

    # === Normalize Type and Detect Workshops ===
    df['Type'] = df['Type'].fillna('other').str.strip().str.lower()
    df.loc[df['Venue'].str.contains("Workshop", case=False, na=False), 'Type'] = 'workshop'

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
        "MIT", "Stanford", "Oxford", "Cambridge", "Harvard",
        "ETH Zurich", "CMU", "Tokyo", "Tsinghua", "Toronto",
        "IBM", "Amazon", "Google", "Microsoft"
    ]
    authors_df['Affiliation'] = [random.choice(affiliations) for _ in range(len(authors_df))]
    authors_df.to_csv(os.path.join(DATA_DIR, "nodes_authors.csv"), index=False)

    # Keywords nodes
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

    # Assign a random keyword to each paper
    titles = df['Title'].unique()
    for t in titles:
        keywords = ["data management", "indexing", "data modeling", "bigdata",
                    "data processing", "data storage", "data querying"]

        df.loc[df['Title'] == t, 'FieldOfStudy'] = random.choice(keywords)


    df['FieldOfStudy'] = df['FieldOfStudy'].apply(safe_literal_eval)

    keywords_df = df.explode('FieldOfStudy')[['FieldOfStudy']].drop_duplicates().rename(columns={
        'FieldOfStudy': 'Keyword'
    })
    keywords_df = keywords_df[keywords_df['Keyword'].notna() & (keywords_df['Keyword'] != '')]
    keywords_df['KeywordID'] = keywords_df['Keyword'].factorize()[0].astype(str)
    keywords_df = keywords_df[['KeywordID', 'Keyword']]
    keywords_df.to_csv(os.path.join(DATA_DIR, "nodes_keywords.csv"), index=False)

    # === SYNTHETIC MULTI-YEAR CONFERENCES & WORKSHOPS ===
    conference_years = [2020, 2021, 2022, 2023]
    workshop_years = [2020, 2021, 2022, 2023]

    original_conference_df = df[df['Type'] == 'conference'][['Venue']].drop_duplicates()
    conference_rows = []
    for venue in original_conference_df['Venue'].unique():
        for year in conference_years:
            conference_rows.append({'Venue': venue, 'Year': year})
    conference_df = pd.DataFrame(conference_rows).drop_duplicates()
    conference_df['ConferenceID'] = conference_df['Venue'].factorize()[0].astype(str)
    conference_df = conference_df[['ConferenceID', 'Venue', 'Year']]
    conference_df.to_csv(os.path.join(DATA_DIR, "nodes_conference.csv"), index=False)

    original_workshop_df = df[df['Type'] == 'workshop'][['Venue']].drop_duplicates()
    workshop_rows = []
    for venue in original_workshop_df['Venue'].unique():
        for year in workshop_years:
            workshop_rows.append({'Venue': venue, 'Year': year})
    workshop_df = pd.DataFrame(workshop_rows).drop_duplicates()
    workshop_df['WorkshopID'] = workshop_df['Venue'].factorize()[0].astype(str)
    workshop_df = workshop_df[['WorkshopID', 'Venue', 'Year']]
    workshop_df.to_csv(os.path.join(DATA_DIR, "nodes_workshop.csv"), index=False)

    # Reassign random Year to each paper to match new synthetic editions
    df.loc[df['Type'] == 'conference', 'Year'] = df[df['Type'] == 'conference']['Venue'].apply(lambda v: random.choice(conference_years))
    df.loc[df['Type'] == 'workshop', 'Year'] = df[df['Type'] == 'workshop']['Venue'].apply(lambda v: random.choice(workshop_years))

    # === Force some authors to publish in same venue in 4 different years ===
    print("Injecting authors into 4 editions of the same venue...")

    # Pick a few authors
    repeat_authors = authors_df['AuthorID'].sample(n=5, random_state=42).tolist()
    # Pick a few venues
    repeat_venues = conference_df['Venue'].unique()[:2]  # use 2 example venues

    extra_author_rows = []

    for author in repeat_authors:
        for venue in repeat_venues:
            for year in [2020, 2021, 2022, 2023]:
                # Get a paper from this venue+year
                paper_row = df[(df['Venue'] == venue) & (df['Year'] == year)].sample(n=1, random_state=random.randint(1, 1000))
                if not paper_row.empty:
                    paper_id = paper_row['PaperId'].values[0]
                    extra_author_rows.append({'AuthorID': author, 'PaperID': paper_id})

    # Combine with existing AUTHOR_OF
    existing_author_of = df[['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
        'AuthorId': 'AuthorID',
        'PaperId': 'PaperID'
    })
    author_of_df = pd.concat([existing_author_of, pd.DataFrame(extra_author_rows)], ignore_index=True).drop_duplicates()
    author_of_df.to_csv(os.path.join(DATA_DIR, "rel_author_of.csv"), index=False)

    # Journal nodes
    journal_df = df[df['Type'] == 'journal'][['Venue', 'Year', 'Volume']].drop_duplicates()
    journal_df['JournalID'] = journal_df['Venue'].factorize()[0].astype(str)
    journal_df['Volume'] = pd.to_numeric(journal_df['Volume'], errors='coerce').fillna(0).astype(int)
    journal_df = journal_df[['JournalID', 'Venue', 'Year', 'Volume']]
    journal_df.to_csv(os.path.join(DATA_DIR, "nodes_journal.csv"), index=False)

    # === RELATIONSHIPS ===

    # AUTHOR_OF
    #df[['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
     #   'AuthorId': 'AuthorID',
      #  'PaperId': 'PaperID'
    #}).to_csv(os.path.join(DATA_DIR, "rel_author_of.csv"), index=False)

    # CORRESPONDING_AUTHOR
    df[df['Main_Author'] == 1][['AuthorId', 'PaperId']].drop_duplicates().rename(columns={
        'AuthorId': 'AuthorID',
        'PaperId': 'PaperID'
    }).to_csv(os.path.join(DATA_DIR, "rel_corresponding_author.csv"), index=False)

    # ABOUT
    keywords_map = dict(zip(keywords_df['Keyword'], keywords_df['KeywordID']))
    df_about = df.explode('FieldOfStudy')[['PaperId', 'FieldOfStudy']].drop_duplicates()
    df_about['KeywordID'] = df_about['FieldOfStudy'].map(keywords_map)
    df_about = df_about.rename(columns={'PaperId': 'PaperID'})[['PaperID', 'KeywordID']]
    df_about.to_csv(os.path.join(DATA_DIR, "rel_about.csv"), index=False)

    # RELATED
    df[['PaperId', 'ReferenceId']].dropna().drop_duplicates().rename(columns={
        'PaperId': 'PaperID',
        'ReferenceId': 'RelatedToPaperID'
    }).to_csv(os.path.join(DATA_DIR, "rel_related.csv"), index=False)

    # PUBLISHED_IN Conference
    df[df['Type'] == 'conference'][['PaperId', 'Venue', 'Year']].merge(
        conference_df[['ConferenceID', 'Venue', 'Year']], on=['Venue', 'Year']
    )[['PaperId', 'ConferenceID']].drop_duplicates().rename(columns={'PaperId': 'PaperID'}).to_csv(
        os.path.join(DATA_DIR, "rel_published_in_conference.csv"), index=False)

    # PUBLISHED_IN Workshop
    df[df['Type'] == 'workshop'][['PaperId', 'Venue', 'Year']].merge(
        workshop_df[['WorkshopID', 'Venue', 'Year']], on=['Venue', 'Year']
    )[['PaperId', 'WorkshopID']].drop_duplicates().rename(columns={'PaperId': 'PaperID'}).to_csv(
        os.path.join(DATA_DIR, "rel_published_in_workshop.csv"), index=False)

    # PUBLISHED_IN Journal
    df[df['Type'] == 'journal'][['PaperId', 'Venue', 'Year']].merge(
        journal_df[['JournalID', 'Venue', 'Year']], on=['Venue', 'Year']
    )[['PaperId', 'JournalID']].drop_duplicates().rename(columns={'PaperId': 'PaperID'}).to_csv(
        os.path.join(DATA_DIR, "rel_published_in_journal.csv"), index=False)
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

if __name__ == '__main__':
    main()