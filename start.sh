#!/bin/bash

# Define the network topology
# 1 - Mesh Network Topology
# 2 - Star Network Topology
# 3 - Tree Network Topology
# 4 - Hierarchical Network Topology
# 5 - Hierarchical Network Topology
# 6 - HLF Distributed Topology
# 7 - Mesh Vector Topology
# 8 - Star Vector Topology
TOPOLOGY_CHOICE=1

# Function to get the current filename
get_filename() {
    filename="$(basename "$PWD")"
    node="${filename%.conf}"
}

# Function for executing the script for Mesh Network Topology
mesh_topology() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/mesh/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
mesh_vector_topology() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/Algorithms/meshV/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
	

# Function for executing the script for Star Network Topology
star_topology() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/star/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
star_vector_topology() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/Algorithms/starV/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}


# Function for executing the script for Tree Network Topology
tree_topology() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/Algorithms/tree/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
hlf_mesh() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/hlf-mesh/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
hlf_proper() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/hlf/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}
hlf_distributed() {
    get_filename
    pythonScriptPath="/home/whoami/Documents/DistributedConsensusAlgorithm/hlf-distributed/main$node.py"
    logPath="/home/whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" 2>&1 | while IFS= read -r line; do echo "$(date +"[%Y-%m-%d %H:%M:%S.%3N]") $line"; done > "$logPath"
}

# Decide which function to call based on topology choice
case $TOPOLOGY_CHOICE in
    1) mesh_topology ;;
    2) star_topology ;;
    3) tree_topology ;;
    4) hlf_mesh ;;
    5) hlf_proper ;;
    6) hlf_distributed ;;
    7) mesh_vector_topology ;;
    8) star_vector_topology ;;
    *) echo "Invalid topology choice"; exit 1 ;;
esac
