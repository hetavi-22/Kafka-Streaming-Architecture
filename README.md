# Kafka Streaming Architecture - NYC Taxi Data Pipeline

A real-time data streaming pipeline that processes NYC taxi trip data using Apache Kafka and Neo4j. This project demonstrates a complete streaming architecture deployed on Kubernetes, where data flows from Parquet files through Kafka topics and into a Neo4j graph database for advanced analytics.

## 🏗️ Architecture Overview

```markdown:/Users/hetavimehta/Desktop/ASU_Acad/Fall2025/CSE511/Project/Project-2/README.md
<code_block_to_apply_changes_from>
Parquet File → Kafka Producer → Kafka Topic → Kafka Connect → Neo4j Graph Database
```

The pipeline consists of:
- **Zookeeper**: Coordination service for Kafka
- **Apache Kafka**: Distributed streaming platform
- **Neo4j**: Graph database for storing trip relationships
- **Kafka Connect**: Connector framework for streaming data from Kafka to Neo4j
- **Data Producer**: Python script that reads Parquet files and streams data to Kafka

## 📋 Prerequisites

Before running this project, ensure you have the following installed:

- **Minikube** (for local Kubernetes cluster)
- **kubectl** (Kubernetes command-line tool)
- **Helm** (Kubernetes package manager)
- **Python 3.x** with pip
- **Python packages**: `confluent-kafka`, `pyarrow`, `pandas`, `neo4j`

### Installation Commands

```bash
# Install Minikube (Ubuntu 22.04)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Helm
sudo snap install helm --classic

# Install kubectl
sudo snap install kubectl --classic

# Add Neo4j Helm repository
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update

# Install Python dependencies
pip install confluent-kafka pyarrow pandas neo4j

# Download NYC taxi data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet
```

## 🚀 Quick Start

### Step 1: Start Minikube

```bash
minikube start
```

### Step 2: Deploy Infrastructure Components

Deploy Zookeeper and Kafka:

```bash
kubectl apply -f zookeeper-setup.yaml
kubectl apply -f kafka-setup.yaml
```

Wait for pods to be ready:

```bash
kubectl get pods
kubectl get services
```

### Step 3: Deploy Neo4j

```bash
helm install my-neo4j-release neo4j/neo4j -f neo4j-values.yaml
kubectl apply -f neo4j-service.yaml
```

Verify Neo4j deployment:

```bash
kubectl get pods -l app.kubernetes.io/name=neo4j
```

### Step 4: Deploy Kafka-Neo4j Connector

```bash
kubectl apply -f kafka-neo4j-connector.yaml
```

Wait for the connector pod to be ready, then configure it:

```bash
chmod +x setup.sh
./setup.sh
```

### Step 5: Set Up Port Forwarding

Open **two separate terminals** and run:

**Terminal 1 - Kafka:**
```bash
kubectl port-forward svc/kafka-service 9092:9092
```

**Terminal 2 - Neo4j:**
```bash
kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
```

### Step 6: Stream Data to Kafka

In a **third terminal**, run the data producer:

```bash
python3 data_producer.py
```

This script will:
- Read the `yellow_tripdata_2022-03.parquet` file
- Filter trips within the Bronx area
- Stream trip data to the `nyc_taxicab_data` Kafka topic
- Send messages at 0.25-second intervals

### Step 7: Verify Pipeline

Run the test suite to verify everything is working:

```bash
python3 tester.py
```

## 📁 Project Structure

```
Project-2/
├── data_producer.py              # Kafka producer that streams Parquet data
├── interface.py                   # Neo4j interface for graph analytics
├── tester.py                     # Comprehensive test suite
├── setup.sh                      # Script to configure Kafka Connect connector
├── sink.neo4j.json               # Kafka Connect Neo4j sink configuration
├── zookeeper-setup.yaml          # Zookeeper Kubernetes deployment
├── kafka-setup.yaml              # Kafka Kubernetes deployment
├── kafka-neo4j-connector.yaml    # Kafka Connect deployment
├── neo4j-service.yaml            # Neo4j Kubernetes service
├── neo4j-values.yaml             # Neo4j Helm chart values
└── README.md                      # This file
```

## 🔧 Configuration Details

### Kafka Topic

- **Topic Name**: `nyc_taxicab_data`
- **Bootstrap Server**: `localhost:9092` (when port-forwarded)

### Data Format

Each message sent to Kafka contains:
```json
{
  "trip_distance": 2.5,
  "PULocationID": 3,
  "DOLocationID": 18,
  "fare_amount": 10.50
}
```

### Neo4j Graph Model

The connector creates the following graph structure:
- **Nodes**: `Location` (with `id` property)
- **Relationships**: `TRIP` (with `distance` and `fare` properties)
- **Cypher Query**: Automatically merges pickup and dropoff locations and creates trip relationships

### Neo4j Connection

- **URI**: `bolt://neo4j-service:7687` (internal) or `bolt://localhost:7687` (port-forwarded)
- **Username**: `neo4j`
- **Password**: `processingpipeline`

## 📊 Graph Analytics

The `interface.py` module provides two graph analytics functions:

### PageRank

Calculates the importance of locations based on trip patterns:

```python
from interface import Interface

interface = Interface("bolt://localhost:7687", "neo4j", "processingpipeline")
results = interface.pageRank("my_project", limit=10)

for record in results:
    print(f"Location: {record['name']}, Score: {record['score']}")
```

### Breadth-First Search (BFS)

Finds the shortest path between two locations:

```python
paths = interface.bfs("3", "18")
for path in paths:
    print(f"Path found: {path}")
```

## 🧪 Testing

The `tester.py` script performs comprehensive testing:

- **Step 1**: Infrastructure tests (Zookeeper, Kafka deployment and connectivity)
- **Step 2**: Neo4j deployment and connectivity
- **Step 3**: Kafka-Neo4j connector deployment
- **Step 4**: Data file validation and producer structure
- **Step 5**: End-to-end pipeline (Kafka messages and Neo4j data)

Run tests:
```bash
python3 tester.py
```

## 🐛 Troubleshooting

### Kafka Connection Issues

- Ensure port-forwarding is active: `kubectl port-forward svc/kafka-service 9092:9092`
- Check Kafka pod status: `kubectl get pods -l app=kafka`
- View Kafka logs: `kubectl logs <kafka-pod-name>`

### Neo4j Connection Issues

- Ensure port-forwarding is active: `kubectl port-forward svc/neo4j-service 7474:7474 7687:7687`
- Check Neo4j pod status: `kubectl get pods -l app.kubernetes.io/name=neo4j`
- Access Neo4j Browser: `http://localhost:7474` (username: `neo4j`, password: `processingpipeline`)

### Connector Issues

- Check connector pod status: `kubectl get pods -l app=kafka-neo4j-connector`
- View connector logs: `kubectl logs <connector-pod-name>`
- Verify connector configuration: `./setup.sh` (checks connector status)

### Data Producer Issues

- Ensure `yellow_tripdata_2022-03.parquet` exists in the current directory
- Verify Kafka port-forwarding is active
- Check that the topic `nyc_taxicab_data` exists or auto-creation is enabled

## 📝 Notes

- The data producer filters trips to only include those within the Bronx area (specific location IDs)
- Trips with distance ≤ 0.1 miles or fare ≤ $2.50 are filtered out
- Messages are sent at 0.25-second intervals to simulate real-time streaming
- The Neo4j connector uses the Graph Data Science (GDS) library for advanced analytics

## 🧹 Cleanup

To remove all deployments:

```bash
kubectl delete -f kafka-neo4j-connector.yaml --ignore-not-found
kubectl delete -f neo4j-service.yaml --ignore-not-found
helm uninstall my-neo4j-release
kubectl delete -f kafka-setup.yaml --ignore-not-found
kubectl delete -f zookeeper-setup.yaml --ignore-not-found
```

## 📄 License

This project is part of an academic course assignment.

## 👤 Author

Created as part of CSE511 course project.

---

**Note**: This project demonstrates a production-ready streaming architecture pattern that can be adapted for various real-time data processing scenarios.
```

## 2. .gitignore

