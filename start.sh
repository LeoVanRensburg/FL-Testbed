#!/bin/bash

# Define the network topology
# 1 - Mesh Network Topology
# 2 - Star Network Topology
# 3 - Tree Network Topology
# 4 - Hierarchical Network Topology
TOPOLOGY_CHOICE=4

# Function to get the current filename
get_filename() {
    filename="$(basename "$PWD")"
    node="${filename%.conf}"
}

# Function for executing the script for Mesh Network Topology
mesh_topology() {
    get_filename
    pythonScriptPath="/home/$whoami/Documents/DistributedConsensusAlgorithm/Algorithms/mesh/main$node.py"
    logPath="/home/$whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" > "$logPath" 2>&1
}

# Function for executing the script for Star Network Topology
star_topology() {
    get_filename
    pythonScriptPath="/home/$whoami/Documents/DistributedConsensusAlgorithm/Algorithms/star/main$node.py"
    logPath="/home/$whoami/Documents/logs/$node/log.txt"
    python3-u "$pythonScriptPath" > "$logPath" 2>&1
}

# Function for executing the script for Tree Network Topology
tree_topology() {
    get_filename
    pythonScriptPath="/home/$whoami/Documents/DistributedConsensusAlgorithm/Algorithms/tree/main$node.py"
    logPath="/home/$whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" > "$logPath" 2>&1
}
hlf_topology() {
    get_filename
    pythonScriptPath="/home/$whoami/Documents/DistributedConsensusAlgorithm/Algorithms/hlf-proper/main$node.py"
    logPath="/home/$whoami/Documents/logs/$node/log.txt"
    python3 -u "$pythonScriptPath" | tee -a "$logPath"
}


# Decide which function to call based on topology choice
case $TOPOLOGY_CHOICE in
    1) mesh_topology ;;
    2) star_topology ;;
    3) tree_topology ;;
    4) hlf_topology ;;
    *) echo "Invalid topology choice"; exit 1 ;;
esac
