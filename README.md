# Neo4j-Research-Publications-Graph-Database
This repository contains the first project for the Semantic Data Management course, part of the Big Data Management and Analytics (BDMA) Master’s program at Universitat Politècnica de Catalunya. The project focuses on graph-based data management using Neo4j.


## Project Structure

| File | Description |
|------|-------------|
| [`data_generation.py`](https://github.com/saracherif123/Neo4j-Research-Publications-Graph-Database/blob/main/data_generation.py) | Generates a synthetic dataset (`papers.csv`) including metadata like authors, venues, and keywords. |
| [`data_preprocessing.py`](https://github.com/saracherif123/Neo4j-Research-Publications-Graph-Database/blob/main/data_preprocessing.py) | Transforms the generated dataset into CSV files suitable for property graph modeling (nodes and relationships). |
| [`load_data_neo4j.py`](https://github.com/saracherif123/Neo4j-Research-Publications-Graph-Database/blob/main/load_data_neo4j.py) | Loads the preprocessed data into a local or remote Neo4j database. |
| `PartA.2_SaadWantland.py` | Defines and explains the project’s property graph schema and assumptions. |
| `PartA.3_SaadWantland.py` | Generates the final `CREATE` Cypher query to construct the full graph. |
| `PartB_SaadWantland.py` | Implements Cypher queries to explore the graph structure (e.g., co-authorship, venue patterns). |
| `PartC_SaadWantland.py` | Adds review-based decision data and models reviewer relationships with papers. |
| `PartD_SaadWantland.py` | Explores advanced graph analytics (e.g., centrality, PageRank) over the scholarly graph. |

---

##  Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/saracherif123/Neo4j-Research-Publications-Graph-Database.git
cd Neo4j-Research-Publications-Graph-Database
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Neo4j

You can either use **Neo4j Desktop** or run Neo4j via **Docker**:

```bash
docker run -d -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/test neo4j:latest
```

---

## 🚀 Run the Project Pipeline

Run the scripts in the following order to complete the pipeline:

 
1. `PartA.2_SaadWantland.py` – Define and explain the property graph schema.  
2. `PartA.3_SaadWantland.py` – Generate and run Cypher `CREATE` statements.  
3. `PartB_SaadWantland.py` – Query co-authorship and venue publication patterns.  
4. `PartC_SaadWantland.py` – Add and query review relationships.  
5. `PartD_SaadWantland.py` – Perform graph analytics (e.g., centrality, PageRank).  

---

## 📌 Notes

- Make sure your Neo4j instance is running before executing any of the loading or querying scripts.  
- Default credentials used in the Docker setup are:  
  ```
  Username: neo4j  
  Password: test
  ```

---

