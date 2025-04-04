from neo4j import GraphDatabase

# Replace these variables with your Neo4j connection details
uri = "bolt://localhost:7692"
username = 'neo4j'
password = 'neo4j123' 

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

def test_nodes_and_relationships():
    with driver.session() as session:
        # Test Paper nodes
        result = session.run("MATCH (p:Paper) RETURN p LIMIT 5")
        print("Paper Nodes:")
        for record in result:
            print(record['p'])

        # Test Author nodes
        result = session.run("MATCH (a:Author) RETURN a LIMIT 5")
        print("\nAuthor Nodes:")
        for record in result:
            print(record['a'])

        # Test Keyword nodes
        result = session.run("MATCH (k:Keyword) RETURN k LIMIT 5")
        print("\nKeyword Nodes:")
        for record in result:
            print(record['k'])

        # Test Conference nodes
        result = session.run("MATCH (c:Conference) RETURN c LIMIT 5")
        print("\nConference Nodes:")
        for record in result:
            print(record['c'])

        # Test Journal nodes
        result = session.run("MATCH (j:Journal) RETURN j LIMIT 5")
        print("\nJournal Nodes:")
        for record in result:
            print(record['j'])

        # Test Workshop nodes
        result = session.run("MATCH (w:Workshop) RETURN w LIMIT 5")
        print("\nWorkshop Nodes:")
        for record in result:
            print(record['w'])

        # Test AUTHOR_OF relationships
        result = session.run("MATCH (a:Author)-[r:AUTHOR_OF]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nAUTHOR_OF Relationships:")
        for record in result:
            print(f"{record['a']} -[:AUTHOR_OF]-> {record['p']}")

        # Test CORRESPONDING_AUTHOR relationships
        result = session.run("MATCH (a:Author)-[r:CORRESPONDING_AUTHOR]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nCORRESPONDING_AUTHOR Relationships:")
        for record in result:
            print(f"{record['a']} -[:CORRESPONDING_AUTHOR]-> {record['p']}")

        # Test ABOUT relationships
        result = session.run("MATCH (p:Paper)-[r:ABOUT]->(k:Keyword) RETURN p, r, k LIMIT 5")
        print("\nABOUT Relationships:")
        for record in result:
            print(f"{record['p']} -[:ABOUT]-> {record['k']}")

        # Test RELATED relationships
        result = session.run("MATCH (p1:Paper)-[r:RELATED]->(p2:Paper) RETURN p1, r, p2 LIMIT 5")
        print("\nRELATED Relationships:")
        for record in result:
            print(f"{record['p1']} -[:RELATED]-> {record['p2']}")

        # Test PUBLISHED_IN relationships for Conferences
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(c:Conference) RETURN p, r, c LIMIT 5")
        print("\nPUBLISHED_IN (Conference) Relationships:")
        for record in result:
            print(f"{record['p']} -[:PUBLISHED_IN]-> {record['c']}")

        # Test PUBLISHED_IN relationships for Journals
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(j:Journal) RETURN p, r, j LIMIT 5")
        print("\nPUBLISHED_IN (Journal) Relationships:")
        for record in result:
            print(f"{record['p']} -[:PUBLISHED_IN]-> {record['j']}")

        # Test PUBLISHED_IN relationships for Workshops
        result = session.run("MATCH (p:Paper)-[r:PUBLISHED_IN]->(w:Workshop) RETURN p, r, w LIMIT 5")
        print("\nPUBLISHED_IN (Workshop) Relationships:")
        for record in result:
            print(f"{record['p']} -[:PUBLISHED_IN]-> {record['w']}")

        # Test REVIEWS relationships
        result = session.run("MATCH (a:Author)-[r:REVIEWS]->(p:Paper) RETURN a, r, p LIMIT 5")
        print("\nREVIEWS Relationships:")
        for record in result:
            print(f"{record['a']} -[:REVIEWS {{Comment: {record['r']['Comment']}, Score: {record['r']['Score']}}}]-> {record['p']}")

# Run the test function
test_nodes_and_relationships()

# Close the driver connection
driver.close()
