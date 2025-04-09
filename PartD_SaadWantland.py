import pprint
from session_helper_neo4j import create_session

# Printing query results and summary 
def print_query_results(records, summary):
    pp = pprint.PrettyPrinter(indent=4)
    print("The query `{}` returned {} records in {} ms.".format(
        summary.query, len(records), summary.result_available_after))
    for record in records:
        pp.pprint(record.data())
        print()

# Algorithm 1: Node Similarity
def query_simulate_node_similarity_algorithm(session):
    print('Dropping the graph from cypher catalog, only if exists')
    session.run("CALL gds.graph.drop('myGraph1',false);")

    print('Project the graph')
    session.run("""
        CALL gds.graph.project('myGraph1', ['Paper','Keyword'], {
            ABOUT: {
                type: 'ABOUT',
                orientation: 'UNDIRECTED'
            }
        });
    """)

    print('Running the node similarity algorithm and writing results')
    session.run("""
        CALL gds.nodeSimilarity.write('myGraph1', {
            writeRelationshipType: 'SIMILAR',
            writeProperty: 'score'
        });
    """)

    print('Fetching top results from SIMILAR relationships')
    result = session.run("""
        MATCH (p1:Paper)-[s:SIMILAR]->(p2:Paper)
        RETURN p1.Title AS Paper1, p2.Title AS Paper2, s.score AS similarity
        ORDER BY similarity DESC
        LIMIT 5;
    """)
    records = list(result)
    summary = result.consume()
    return records, summary

# Algorithm 2: Betweenness Centrality
def query_simulate_betweeneness_centrality_algorithm(session):
    print('Dropping the graph from cypher catalog, only if exists')
    session.run("CALL gds.graph.drop('myGraph2',false);")

    print('Projecting the graph')
    session.run("""
        CALL gds.graph.project('myGraph2', 'Paper', {
            RELATED: {type: 'RELATED', orientation: 'UNDIRECTED'}
        });
    """)

    print('Running the betweenness centrality algorithm for the stored graph')
    session.run("""
        CALL gds.betweenness.write('myGraph2', {
            writeProperty: 'betweenness'
        });
    """)

    result = session.run("""
        CALL gds.betweenness.stream('myGraph2')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).Title AS Title, 
               score
        ORDER BY score DESC, Title
        LIMIT 5;
    """)
    records = list(result)
    summary = result.consume()
    return records, summary

# Algorithm 3: PageRank
def query_simulate_pagerank_algorithm(session):
    print('Dropping PageRank graph if it exists')
    session.run("CALL gds.graph.drop('pagerankGraph', false);")

    print('Projecting the graph for PageRank')
    session.run("""
        CALL gds.graph.project('pagerankGraph', 'Paper', {
            RELATED: {type: 'RELATED', orientation: 'NATURAL'}
        });
    """)

    print('Running PageRank algorithm')
    result = session.run("""
        CALL gds.pageRank.stream('pagerankGraph')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).Title AS Title, score
        ORDER BY score DESC
        LIMIT 5;
    """)
    records = list(result)
    summary = result.consume()
    return records, summary

def main():
    session = create_session()
    print('Algorithm 1 - Node Similarity..........')
    records, summary = session.execute_write(query_simulate_node_similarity_algorithm)
    print_query_results(records, summary)

    print('Algorithm 2 - Betweenness Centrality..........')
    records, summary = session.execute_write(query_simulate_betweeneness_centrality_algorithm)
    print_query_results(records, summary)

    print('Algorithm 3 - PageRank..........')
    records, summary = session.execute_write(query_simulate_pagerank_algorithm)
    print_query_results(records, summary)

    session.close()

if __name__ == '__main__':
    main()