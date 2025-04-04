from neo4j import GraphDatabase
import pprint

# Replace these variables with your Neo4j connection details
uri = "bolt://localhost:7692"
username = 'neo4j'
password = 'neo4j123'

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Helper function for pretty printing
def print_results(result):
    pp = pprint.PrettyPrinter(indent=2)
    for record in result:
        pp.pprint(record.data())


def test_nodes_and_relationships():
    with driver.session() as session:
        # Test Paper nodes
        result = session.run("MATCH (p:Paper) RETURN p LIMIT 5")
        print("Paper Nodes:")
        print_results(result)

        # Test Author nodes
        result = session.run("MATCH (a:Author) RETURN a LIMIT 5")
        print("\nAuthor Nodes:")
        print_results(result)

        # Test Keyword nodes
        result = session.run("MATCH (k:Keyword) RETURN k LIMIT 5")
        print("\nKeyword Nodes:")
        print_results(result)

        # Test Conference nodes
        result = session.run("MATCH (c:Conference) RETURN c LIMIT 5")
        print("\nConference Nodes:")
        print_results(result)

        # Test Journal nodes
        result = session.run("MATCH (j:Journal) RETURN j LIMIT 5")
        print("\nJournal Nodes:")
        print_results(result)

        # Test Workshop nodes
        result = session.run("MATCH (w:Workshop) RETURN w LIMIT 5")
        print("\nWorkshop Nodes:")
        print_results(result)

        # Test AUTHOR_OF relationships
        result = session.run("MATCH (a:Author)-[r:AUTHOR_OF]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nAUTHOR_OF Relationships:")
        print_results(result)

        # Test CORRESPONDING_AUTHOR relationships
        result = session.run("MATCH (a:Author)-[r:CORRESPONDING_AUTHOR]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nCORRESPONDING_AUTHOR Relationships:")
        print_results(result)

        # Test ABOUT relationships
        result = session.run("MATCH (p:Paper)-[r:ABOUT]->(k:Keyword) RETURN p, r, k LIMIT 5")
        print("\nABOUT Relationships:")
        print_results(result)

        # Test RELATED relationships
        result = session.run("MATCH (p1:Paper)-[r:RELATED]->(p2:Paper) RETURN p1, r, p2 LIMIT 5")
        print("\nRELATED Relationships:")
        print_results(result)

        # Test PUBLISHED_IN relationships for Conferences
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(c:Conference) RETURN p, r, c LIMIT 5")
        print("\nPUBLISHED_IN (Conference) Relationships:")
        print_results(result)

        # Test PUBLISHED_IN relationships for Journals
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(j:Journal) RETURN p, r, j LIMIT 5")
        print("\nPUBLISHED_IN (Journal) Relationships:")
        print_results(result)

        # Test PUBLISHED_IN relationships for Workshops
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(w:Workshop) RETURN p, r, w LIMIT 5")
        print("\nPUBLISHED_IN (Workshop) Relationships:")
        print_results(result)

        # Test REVIEWS relationships
        result = session.run("MATCH (a:Author)-[r:REVIEWS]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nREVIEWS Relationships:")
        print_results(result)

        # Test Author → Review → Paper relationships
        print("\nTesting Author → Review → Paper relationships:")
        result = session.run("""
            MATCH (a:Author)-[:WROTE]->(r:Review)-[:REVIEWS]->(p:Paper)
            RETURN a.AuthorID AS reviewer, 
                   p.PaperID AS paper, 
                   r.Score AS score, 
                   r.SuggestedDecision AS decision
            LIMIT 10;
        """)
        print_results(result)

    

# Run the test function
test_nodes_and_relationships()

# Close the driver connection
driver.close()
