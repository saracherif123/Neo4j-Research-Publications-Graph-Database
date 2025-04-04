from session_helper_neo4j import create_session

def load_review_nodes(session):
    session.run("""
        LOAD CSV WITH HEADERS FROM 'file:///data/rel_reviews.csv' AS row
        MATCH (a:Author {AuthorID: row.ReviewerID})
        MATCH (p:Paper {PaperID: row.PaperID})
        CREATE (r:Review {
            Comment: row.Comment,
            Score: toInteger(row.Score),
            SuggestedDecision: CASE
                WHEN toInteger(row.Score) > 3 THEN 'accept'
                ELSE 'reject'
            END
        })
        MERGE (a)-[:WROTE]->(r)
        MERGE (r)-[:REVIEWS]->(p);
    """)

def set_paper_final_decision(session):
    session.run("""
        MATCH (p:Paper)<-[:REVIEWS]-(r:Review)
        WITH p,
            COUNT(CASE WHEN r.SuggestedDecision = 'accept' THEN 1 END) AS acceptCount,
            COUNT(r) AS totalReviews
        SET p.FinalDecision = CASE
            WHEN acceptCount > totalReviews / 2 THEN 'accept'
            ELSE 'reject'
        END;
    """)

def load_institution_nodes(session):
    session.run("""
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_authors.csv' AS row
        MERGE (i:Institution {name: row.Affiliation})
        WITH i, row
        MATCH (a:Author {AuthorID: row.AuthorID})
        MERGE (a)-[:IS_FROM]->(i);
    """)

# Execute all transformations
session = create_session()
print("Loading reviews as nodes...")
session.execute_write(load_review_nodes)

print("Linking authors to institutions...")
session.execute_write(load_institution_nodes)

print("Setting final decisions for each paper...")
session.execute_write(set_paper_final_decision)

session.close()
print("Graph evolution completed.")
