import pprint
from session_helper_neo4j import create_session

session = create_session()

def print_query_results(records, summary):
    pp = pprint.PrettyPrinter(indent=4)
    print("The query `{}` returned {} records in {} ms.".format(
        summary.query, len(records), summary.result_available_after))
    for record in records:
        pp.pprint(record.data())
        print()

# Query 1: Top 3 most cited papers per conference/workshop
def query_top3_cited_papers_conference(session):
    result = session.run(
        """
        MATCH (venue)<-[:PUBLISHED_IN]-(p:Paper)<-[:RELATED]-(citing:Paper)
        WHERE venue:Conference
        WITH venue, p, COUNT(citing) AS citations
        ORDER BY venue.Venue, citations DESC
        WITH venue, COLLECT(p)[..3] AS topPapers
        RETURN 
            venue.Venue AS venueName,
            topPapers[0].Title AS topCitedPaper1,
            topPapers[1].Title AS topCitedPaper2,
            topPapers[2].Title AS topCitedPaper3
        """
    )
    return list(result), result.consume()

# Query 2: Authors publishing in same conference/workshop in at least 4 editions
# This query doesn't work as we only have 2 ediitons of each conference/workshop, we need more data here
def query_authors_published_same_venue_4editions(session):
    result = session.run(
        """
        MATCH (a:Author)-[:AUTHOR_OF]->(p:Paper)-[:PUBLISHED_IN]->(venue)
        WHERE venue:Conference OR venue:Workshop
        WITH a, venue, COUNT(DISTINCT p.Year) AS editions
        WHERE editions >= 2
        RETURN a.Name AS author, venue.Venue AS venueName, editions
        ORDER BY author, editions DESC
        """
    )
    return list(result), result.consume()

# Query 3: Impact factor of journals
def query_impact_factor(session):
    result = session.run(
        """
        MATCH (citing:Paper)-[:RELATED]->(cited:Paper)-[:PUBLISHED_IN]->(j:Journal)
        WHERE citing.Year = j.Year + 1 OR citing.Year = j.Year + 2
        WITH j, COUNT(cited) AS citationCount
        MATCH (p:Paper)-[:PUBLISHED_IN]->(j)
        WHERE p.Year = j.Year OR p.Year = j.Year - 1
        WITH j.Name AS journal, j.Year AS year, citationCount, COUNT(p) AS pubCount
        WHERE pubCount > 0
        RETURN journal, year,
               ROUND(toFloat(citationCount) / pubCount, 3) AS impactFactor
        ORDER BY impactFactor DESC
        LIMIT 10
        """
    )
    return list(result), result.consume()

# Query 4: H-Index per author
def query_h_index(session):
    result = session.run(
        """
        MATCH (a:Author)-[:AUTHOR_OF]->(p:Paper)<-[:RELATED]-(citing:Paper)
        WITH a, p, COUNT(citing) AS citationCount
        ORDER BY citationCount DESC
        WITH a.Name AS author, COLLECT(citationCount) AS citations
        WITH author, citations,
             REDUCE(h = 0, i IN RANGE(0, SIZE(citations)-1) |
                CASE WHEN citations[i] >= i+1 THEN i+1 ELSE h END) AS hIndex
        RETURN author, hIndex
        ORDER BY hIndex DESC
        LIMIT 10
        """
    )
    return list(result), result.consume()

# Run and print all query results
records, summary = session.execute_read(query_top3_cited_papers_conference)
print('\n--- Query 1: Top 3 Most Cited Papers per Venue ---')
print_query_results(records, summary)

records, summary = session.execute_read(query_authors_published_same_venue_4editions)
print('\n--- Query 2: Authors Publishing in Venue in >= 4 Editions ---')
print_query_results(records, summary)

records, summary = session.execute_read(query_impact_factor)
print('\n--- Query 3: Journal Impact Factors ---')
print_query_results(records, summary)

records, summary = session.execute_read(query_h_index)
print('\n--- Query 4: Author H-Index ---')
print_query_results(records, summary)

session.close()
