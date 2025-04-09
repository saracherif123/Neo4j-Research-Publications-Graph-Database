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

# Deletes the now unnecessary review relationship between author and paper
def del_review_relation(session):
    session.run("""
        MATCH(m:Author)-[r:REVIEWS]->() delete r;
    """)

# This query sets the final decision for each paper based on the reviews.
# If more than half of the reviews suggest acceptance, the paper is accepted.
# Otherwise, it is rejected.
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

def load_affiliation_as_property(session):
    session.run("""
        LOAD CSV WITH HEADERS FROM 'file:///data/nodes_authors.csv' AS row
        MATCH (a:Author {AuthorID: row.AuthorID})
        SET a.Affiliation = row.Affiliation;
    """)

def main():
    # Execute all transformations
    session = create_session()
    print("Loading reviews as nodes...")
    session.execute_write(load_review_nodes)

    print("Deleting review relationship...")
    session.execute_write(del_review_relation)

    print("Linking authors to institutions...")
    session.execute_write(load_affiliation_as_property)

    print("Setting final decisions for each paper...")
    session.execute_write(set_paper_final_decision)

    session.close()
    print("Graph evolution completed.")

if __name__ == '__main__':
    main()