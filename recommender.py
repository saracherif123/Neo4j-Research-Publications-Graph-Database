import pprint
from session_helper_neo4j import create_session

session = create_session()

# Helper to print query results
def print_query_results(records, summary):
    pp = pprint.PrettyPrinter(indent=4)
    print("The query `{}` returned {} records in {} ms.".format(
        summary.query, len(records), summary.result_available_after))
    for record in records:
        pp.pprint(record.data())
        print()

# Stage 1: Define the Databases research community and link relevant keywords
def stage1_define_community(session):
    result = session.run("""
        MERGE (rc:ResearchCommunity {name: "Databases"})
        WITH rc
        UNWIND ["Data Management", "Indexing", "Data Modeling", "Big Data", "Data Processing", "Data Storage", "Data Querying"] AS keyword
        MATCH (k:Keyword) WHERE toLower(k.Keyword) = toLower(keyword)
        MERGE (k)-[:BELONGS_TO]->(rc)
        RETURN rc.name AS community, collect(k.Keyword) AS linkedKeywords;
    """)
    records = list(result)
    summary = result.consume()
    print_query_results(records, summary)

# Stage 2: Identify publication venues strongly tied to the Databases community
def stage2_mark_database_venues(session):
    result = session.run("""
        MATCH (rc:ResearchCommunity {name: "Databases"})<-[:BELONGS_TO]-(k:Keyword)<-[:ABOUT]-(p:Paper)
        WITH DISTINCT p
        MATCH (p)-[:PUBLISHED_IN]->(v)
        WHERE v:Conference OR v:Journal OR v:Workshop
        WITH v, COUNT(DISTINCT p) AS communityPapers
        MATCH (p2:Paper)-[:PUBLISHED_IN]->(v)
        WITH v, communityPapers, COUNT(DISTINCT p2) AS totalPapers
        WHERE toFloat(communityPapers)/toFloat(totalPapers) >= 0.9
        SET v:DatabaseVenue
        RETURN v.Name AS venueName, communityPapers, totalPapers;
    """)
    records = list(result)
    summary = result.consume()
    print_query_results(records, summary)

# Stage 3: Identify top 100 cited papers in database venues
def stage3_mark_top100_papers(session):
    result = session.run("""
        MATCH (p:Paper)-[:PUBLISHED_IN]->(v:DatabaseVenue)
        OPTIONAL MATCH (other:Paper)-[:CITES]->(p)
        WITH p, COUNT(other) AS citationCount
        ORDER BY citationCount DESC
        WITH COLLECT({title: p.Title, citations: citationCount})[0..100] AS topPapers
        UNWIND topPapers AS tp
        MATCH (paper:Paper {Title: tp.title})
        SET paper:TopPaper
        RETURN paper.Title AS paperTitle, tp.citations AS citations;
    """)
    records = list(result)
    summary = result.consume()
    print_query_results(records, summary)

# Stage 4: Mark authors as reviewers or gurus based on top papers
def stage4_mark_reviewers_and_gurus(session):
    result = session.run("""
        MATCH (a:Author)-[:AUTHOR_OF]->(p:TopPaper)
        WITH a, COUNT(p) AS topPapersWritten
        SET a:PotentialReviewer
        WITH a, topPapersWritten
        WHERE topPapersWritten >= 2
        SET a:Guru
        RETURN a.Name AS authorName, topPapersWritten, labels(a) AS labels;
    """)
    records = list(result)
    summary = result.consume()
    print_query_results(records, summary)

# Execute all stages with outputs
print("\nStage 1: Defining research community and linking keywords...")
session.execute_write(stage1_define_community)

print("\nStage 2: Marking database-specific venues...")
session.execute_write(stage2_mark_database_venues)

print("\nStage 3: Identifying top-100 papers...")
session.execute_write(stage3_mark_top100_papers)

print("\nStage 4: Identifying potential reviewers and gurus...")
session.execute_write(stage4_mark_reviewers_and_gurus)

print("\nAll stages executed successfully.")
session.close()