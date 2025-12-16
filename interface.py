from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def pageRank(self, project_name, limit=10):
        """
        Calculates PageRank using the Neo4j Graph Data Science (GDS) library.
        Required by Step 4 of the project.
        """
        with self.driver.session() as session:
            # 1. Clean up: Check if the graph projection already exists, and drop it if so
            session.run(f"""
                CALL gds.graph.exists('{project_name}') 
                YIELD exists 
                WITH exists 
                WHERE exists 
                CALL gds.graph.drop('{project_name}') 
                YIELD graphName 
                RETURN graphName
            """)

            # 2. Project the graph: Create an in-memory graph for GDS
            # We project 'Location' nodes and 'TRIP' relationships
            session.run(f"""
                CALL gds.graph.project(
                    '{project_name}',
                    'Location',
                    'TRIP',
                    {{ relationshipProperties: 'weight' }}
                )
            """)

            # 3. Run PageRank Stream
            result = session.run(f"""
                CALL gds.pageRank.stream('{project_name}')
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC, name ASC
                LIMIT {limit}
            """)
            
            return [record for record in result]

    def bfs(self, start_node, end_node):
        """
        Performs Breadth-First Search (BFS) to find the shortest path.
        Required by Step 4 of the project.
        """
        with self.driver.session() as session:
            # Using standard Cypher ShortestPath which implements BFS logic
            result = session.run("""
                MATCH (start:Location {name: $start_node}), (end:Location {name: $end_node})
                MATCH path = shortestPath((start)-[:TRIP*]-(end))
                RETURN path
            """, start_node=start_node, end_node=end_node)
            
            return [record["path"] for record in result]