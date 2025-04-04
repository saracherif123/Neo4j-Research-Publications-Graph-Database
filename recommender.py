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
    session.run("""
        MERGE (rc:ResearchCommunity {name: "Databases"})
        WITH rc
        UNWIND ["Data Management", "Indexing", "Data Modeling", "Big Data", "Data Processing", "Data Storage", "Data Querying"] AS keyword
        MATCH (k:Keyword) WHERE toLower(k.Keyword) = toLower(keyword)
        MERGE (k)-[:BELONGS_TO]->(rc);
    """)

# Stage 2: Identify publication venues strongly tied to the Databases community

def stage2_mark_database_venues(session):
    session.run("""
        MATCH (rc:ResearchCommunity {name: "Databases"})<-[:BELONGS_TO]-(k:Keyword)<-[:ABOUT]-(p:Paper)
        WITH DISTINCT p
        MATCH (p)-[:PUBLISHED_IN]->(v)
        WHERE v:Conference OR v:Journal OR v:Workshop
        WITH v, COUNT(DISTINCT p) AS communityPapers
        MATCH (p2:Paper)-[:PUBLISHED_IN]->(v)
        WITH v, communityPapers, COUNT(DISTINCT p2) AS totalPapers
        WHERE toFloat(communityPapers)/toFloat(totalPapers) >= 0.9
        SET v:DatabaseVenue;
    """)

# Stage 3: Identify top 100 cited papers in database venues

def stage3_mark_top100_papers(session):
    session.run("""
        MATCH (p:Paper)-[:PUBLISHED_IN]->(v:DatabaseVenue)
        OPTIONAL MATCH (other:Paper)-[:CITES]->(p)
        WITH p, COUNT(other) AS citationCount
        ORDER BY citationCount DESC
        WITH COLLECT(p)[0..100] AS topPapers
        UNWIND topPapers AS tp
        SET tp:TopPaper;
    """)

# Stage 4: Mark authors as reviewers or gurus based on top papers

def stage4_mark_reviewers_and_gurus(session):
    session.run("""
        MATCH (a:Author)-[:AUTHOR_OF]->(p:TopPaper)
        WITH a, COUNT(p) AS topPapersWritten
        SET a:PotentialReviewer
        WITH a, topPapersWritten
        WHERE topPapersWritten >= 2
        SET a:Guru;
    """)

# Execute all stages
print("Stage 1: Defining research community and linking keywords...")
session.execute_write(stage1_define_community)

print("Stage 2: Marking database-specific venues...")
session.execute_write(stage2_mark_database_venues)

print("Stage 3: Identifying top-100 papers...")
session.execute_write(stage3_mark_top100_papers)

print("Stage 4: Identifying potential reviewers and gurus...")
session.execute_write(stage4_mark_reviewers_and_gurus)

print("All stages executed successfully.")
session.close()
