#!/bin/bash

# Define the network topology
# 1 - Mesh Network Topology
# 2 - Star Network Topology
# 3 - Tree Network Topology
# 4 - HLF Distributed Topology
TOPOLOGY_CHOICE=4

# Function to get the current filename
get_filename() {
    filename="$(basename "$PWD")"
    node="${filename%.conf}"
}

# Function for executing the script for Mesh Network Topology
mesh_topology() {
    get_filename
    pythonScriptPath="/home/leo/Documents/DistributedConsensusAlgorithm/Algorithms/consensus_node.py"
    logPath="/home/leo/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" mesh $node 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
	
# Function for executing the script for Star Network Topology
star_topology() {
    get_filename
    pythonScriptPath="/home/leo/Documents/DistributedConsensusAlgorithm/Algorithms/consensus_node.py"
    logPath="/home/leo/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" star $node 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}

# Function for executing the script for Tree Network Topology
tree_topology() {
    get_filename
    pythonScriptPath="/home/leo/Documents/DistributedConsensusAlgorithm/Algorithms/consensus_node.py"
    logPath="/home/leo/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" tree $node 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}

hlf_distributed() {
    get_filename
    pythonScriptPath="/home/leo/Documents/DistributedConsensusAlgorithm/Algorithms/consensus_node.py"
    logPath="/home/leo/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" hlf $node 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}

# Decide which function to call based on topology choice
case $TOPOLOGY_CHOICE in
    1) mesh_topology ;;
    2) star_topology ;;
    3) tree_topology ;;
    4) hlf_distributed ;;
    *) echo "Invalid topology choice!@"; exit 1 ;;
esac
