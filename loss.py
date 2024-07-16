import subprocess
import sys

# Define topologies
STAR_TOPOLOGY = {
    '1': [('7', 0, 0)],
    '2': [('7', 0, 1)],
    '3': [('7', 0, 2)],
    '4': [('7', 0, 3)],
    '5': [('7', 0, 4)]
}

MESH_TOPOLOGY = {
    '1': [('2', 0, 0), ('3', 1, 0), ('4', 2, 0), ('5', 3, 0)],
    '2': [('1', 0, 0), ('3', 1, 1), ('4', 3, 1), ('5', 2, 1)],
    '3': [('1', 0, 1), ('2', 1, 1), ('4', 2, 2), ('5', 3, 3)],
    '4': [('1', 0, 2), ('2', 1, 3), ('3', 2, 2), ('5', 3, 2)],
    '5': [('1', 0, 3), ('2', 1, 2), ('3', 3, 3), ('4', 2, 3)]
}

TREE_TOPOLOGY = {
    '1': [('2', 0, 0), ('3', 1, 0)],
    '2': [('1', 0, 0)],
    '3': [('1', 0, 1), ('4', 1, 0), ('5', 2, 0)],
    '4': [('3', 0, 1)],
    '5': [('3', 0, 2)]
}

HLF_TOPOLOGY = {
    '1': [('2', 0, 0), ('3', 1, 0), ('4', 2, 2)],
    '2': [('1', 0, 0), ('3', 1, 1), ('4', 2, 0)],
    '3': [('1', 0, 1), ('2', 1, 1), ('4', 2, 1)],
    '4': [('1', 2, 2), ('2', 0, 2), ('3', 1, 2), ('13', 3, 1)],
    '5': [('6', 0, 0), ('7', 1, 1), ('8', 2, 2)],
    '6': [('5', 0, 0), ('7', 2, 2), ('8', 1, 0)],
    '7': [('5', 1, 1), ('6', 2, 2), ('8', 0, 1), ('13', 3, 0)],
    '8': [('5', 2, 2), ('6', 0, 1), ('7', 1, 0)],
    '9': [('10', 0, 0), ('11', 1, 1), ('12', 2, 2), ('13', 3, 2)],
    '10': [('9', 0, 0), ('11', 2, 2), ('12', 1, 0)],
    '11': [('9', 1, 1), ('10', 2, 2), ('12', 0, 1)],
    '12': [('9', 2, 2), ('10', 0, 1), ('11', 1, 0)],
    '13': [('4', 1, 3), ('7', 0, 3), ('9', 2, 3)]
}

def apply_packet_loss(session_id, node, loss, topology):
    if node not in topology:
        print(f"No connections found for node {node} in the selected topology")
        return

    for connected_node, interface1, interface2 in topology[node]:
        command = f"core-cli link -s {session_id} edit -n1 {node} -n2 {connected_node} -i1 {interface1} -i2 {interface2} -l {loss}"

        print(f"Executing command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"Command output: {result.stdout}")
            print(f"Applied {loss}% packet loss between node {node} and node {connected_node}")
        except subprocess.CalledProcessError as e:
            print(f"Error applying packet loss: {e}")
            print(f"Error output: {e.stderr}")

def main():
    if len(sys.argv) < 5:
        print("Usage: python script.py <session_id> <topology: star|mesh|tree|hlf> <comma_separated_nodes> <packet_loss_percentage>")
        sys.exit(1)

    session_id = sys.argv[1]
    topology_name = sys.argv[2].lower()
    nodes = sys.argv[3].split(',')
    loss = sys.argv[4]

    if topology_name == 'star':
        topology = STAR_TOPOLOGY
    elif topology_name == 'mesh':
        topology = MESH_TOPOLOGY
    elif topology_name == 'tree':
        topology = TREE_TOPOLOGY
    elif topology_name == 'hlf':
        topology = HLF_TOPOLOGY
    else:
        print(f"Unknown topology: {topology_name}. Please choose 'star', 'mesh', 'tree', or 'hlf'.")
        sys.exit(1)

    print(f"Starting script with session_id: {session_id}, topology: {topology_name}, nodes: {nodes}, loss: {loss}")

    for node in nodes:
        apply_packet_loss(session_id, node.strip(), loss, topology)

if __name__ == "__main__":
    main()
