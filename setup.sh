#!/bin/bash

POD_NAME=$(kubectl get pods -l app=kafka-neo4j-connector -o jsonpath="{.items[0].metadata.name}")

echo "Found Connector Pod: $POD_NAME"

echo "Starting port-forward to $POD_NAME..."
kubectl port-forward $POD_NAME 8083:8083 &

PID=$!

sleep 5

echo "Posting configuration to Kafka Connect..."
curl -X POST -H "Content-Type: application/json" --data @sink.neo4j.json http://localhost:8083/connectors

echo -e "\nConfiguration sent."

kill $PID
echo "Port-forwarding stopped."

echo "Checking connector status..."
kubectl port-forward $POD_NAME 8083:8083 &
PID_CHECK=$!
sleep 5
curl http://localhost:8083/connectors/Neo4jSink_v2/status
kill $PID_CHECK
