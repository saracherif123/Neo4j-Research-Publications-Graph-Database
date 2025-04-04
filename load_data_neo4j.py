from session_helper_neo4j import create_session, clean_session

def load_node_papers(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_papers.csv' AS line
        CREATE (:Paper {
            PaperID: line.PaperID,
            Title: line.Title,
            Year: toInteger(line.Year),
            Abstract: line.Abstract,
            DOI: line.DOI
        })
        """
    )

def load_node_authors(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_authors.csv' AS line
        CREATE (:Author {
            AuthorID: line.AuthorID,
            Name: line.Name,
            Affiliation: line.Affiliation
        })
        """
    )

def load_node_keywords(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_keywords.csv' AS line
        CREATE (:Keyword {
            KeywordID: line.KeywordID,
            Keyword: line.Keyword
        })
        """
    )

def load_node_conferences(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_conference.csv' AS line
        CREATE (:Conference {
            ConferenceID: line.ConferenceID,
            Venue: line.Venue,
            Year: toInteger(line.Year)
        })
        """
    )

def load_node_journals(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_journal.csv' AS line
        CREATE (:Journal {
            JournalID: line.JournalID,
            Venue: line.Venue,
            Year: toInteger(line.Year),
            Volume: toInteger(line.Volume)
        })
        """
    )

def load_node_workshops(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_workshop.csv' AS line
        CREATE (:Workshop {
            WorkshopID: line.WorkshopID,
            Venue: line.Venue,
            Year: toInteger(line.Year)
        })
        """
    )

def load_rel_author_of(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_author_of.csv' AS line
        MATCH (a:Author {AuthorID: line.AuthorID})
        MATCH (p:Paper {PaperID: line.PaperID})
        CREATE (a)-[:AUTHOR_OF]->(p)
        """
    )

def load_rel_corresponding_author(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_corresponding_author.csv' AS line
        MATCH (a:Author {AuthorID: line.AuthorID})
        MATCH (p:Paper {PaperID: line.PaperID})
        CREATE (a)-[:CORRESPONDING_AUTHOR]->(p)
        """
    )

def load_rel_about(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_about.csv' AS line
        MATCH (p:Paper {PaperID: line.PaperID})
        MATCH (k:Keyword {KeywordID: line.KeywordID})
        CREATE (p)-[:ABOUT]->(k)
        """
    )

def load_rel_related(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_related.csv' AS line
        MATCH (p1:Paper {PaperID: line.PaperID})
        MATCH (p2:Paper {PaperID: line.RelatedToPaperID})
        CREATE (p1)-[:RELATED]->(p2)
        """
    )

def load_rel_published_in_conference(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_published_in_conference.csv' AS line
        MATCH (p:Paper {PaperID: line.PaperID})
        MATCH (c:Conference {ConferenceID: line.ConferenceID})
        CREATE (p)-[:PUBLISHED_IN]->(c)
        """
    )

def load_rel_published_in_journal(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_published_in_journal.csv' AS line
        MATCH (p:Paper {PaperID: line.PaperID})
        MATCH (j:Journal {JournalID: line.JournalID})
        CREATE (p)-[:PUBLISHED_IN]->(j)
        """
    )

def load_rel_published_in_workshop(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_published_in_workshop.csv' AS line
        MATCH (p:Paper {PaperID: line.PaperID})
        MATCH (w:Workshop {WorkshopID: line.WorkshopID})
        CREATE (p)-[:PUBLISHED_IN]->(w)
        """
    )

def load_rel_reviews(session):
    session.run(
        """
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_reviews.csv' AS line
        MATCH (a:Author {AuthorID: line.ReviewerID})
        MATCH (p:Paper {PaperID: line.PaperID})
        CREATE (a)-[:REVIEWS {
            Comment: line.Comment,
            Score: toInteger(line.Score)
        }]->(p)
        """
    )

if __name__ == '__main__':
    session = create_session()
    session = clean_session(session)

    print("Loading nodes...")
    session.execute_write(load_node_papers)
    session.execute_write(load_node_authors)
    session.execute_write(load_node_keywords)
    session.execute_write(load_node_conferences)
    session.execute_write(load_node_journals)
    session.execute_write(load_node_workshops)

    print("Loading relationships...")
    session.execute_write(load_rel_author_of)
    session.execute_write(load_rel_corresponding_author)
    session.execute_write(load_rel_about)
    session.execute_write(load_rel_related)
    session.execute_write(load_rel_published_in_conference)
    session.execute_write(load_rel_published_in_journal)
    session.execute_write(load_rel_published_in_workshop)
    session.execute_write(load_rel_reviews)

    print("Done loading all data into Neo4j.")
    session.close()
