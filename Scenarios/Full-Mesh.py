import re

def modify_start_sh():
    file_path = '/home/whoami/Documents/DistributedConsensusAlgorithm/start.sh'
    variable_name = 'TOPOLOGY_CHOICE'
    new_value = '1'

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith(variable_name + '='):
            lines[i] = re.sub(rf'{variable_name}=\d', f'{variable_name}={new_value}', line)
            break

    with open(file_path, 'w') as file:
        file.writelines(lines)

# Call the function to modify the start.sh file
modify_start_sh()

from core.api.grpc import client
from core.api.grpc.wrappers import Position, NodeType

def main():
    # interface helper
    iface_helper = client.InterfaceHelper(
        ip4_prefix="10.0.0.0/24",
        ip6_prefix="2001::/64",
    )

    # create grpc client and connect
    core = client.CoreGrpcClient()
    core.connect()

    # create session
    session = core.create_session()

    # create nodes
    node_positions = [
        Position(x=356.0, y=63.0),
        Position(x=580.0, y=170.0),
        Position(x=528.0, y=407.0),
        Position(x=246.0, y=401.0),
        Position(x=137.0, y=168.0),
    ]

    nodes = []
    for node_id, position in enumerate(node_positions, start=1):
        node = session.add_node(_id=node_id, name=str(node_id), position=position)
        node.services.add("Distributed Consensus Algorithm")
        node.services.add("Node Startup Script")
        node.services.add("DefaultRoute")
        nodes.append(node)

    # create links
    link_config = [
        (0, 1, 0, 0, "10.0.0.20", "10.0.0.21", "2001::14", "2001::15"),
        (0, 2, 1, 0, "10.0.1.20", "10.0.1.21", "2001:0:0:1::14", "2001:0:0:1::15"),
        (0, 3, 2, 0, "10.0.2.20", "10.0.2.21", "2001:0:0:2::14", "2001:0:0:2::15"),
        (0, 4, 3, 0, "10.0.3.20", "10.0.3.21", "2001:0:0:3::14", "2001:0:0:3::15"),
        (1, 2, 1, 1, "10.0.4.20", "10.0.4.21", "2001:0:0:4::14", "2001:0:0:4::15"),
        (1, 4, 2, 1, "10.0.5.20", "10.0.5.21", "2001:0:0:5::14", "2001:0:0:5::15"),
        (2, 3, 2, 2, "10.0.7.20", "10.0.7.21", "2001:0:0:7::14", "2001:0:0:7::15"),
        (1, 3, 3, 1, "10.0.6.20", "10.0.6.21", "2001:0:0:6::14", "2001:0:0:6::15"),
        (3, 4, 3, 2, "10.0.8.20", "10.0.8.21", "2001:0:0:8::14", "2001:0:0:8::15"),
        (2, 4, 3, 3, "10.0.9.20", "10.0.9.21", "2001:0:0:9::14", "2001:0:0:9::15"),
    ]

    for node1_idx, node2_idx, iface1_id, iface2_id, ip4_1, ip4_2, ip6_1, ip6_2 in link_config:
        node1 = nodes[node1_idx]
        node2 = nodes[node2_idx]
        iface1 = iface_helper.create_iface(node_id=node1.id, iface_id=iface1_id)
        iface1.ip4 = ip4_1
        iface1.ip6 = ip6_1
        iface2 = iface_helper.create_iface(node_id=node2.id, iface_id=iface2_id)
        iface2.ip4 = ip4_2
        iface2.ip6 = ip6_2
        session.add_link(node1=node1, node2=node2, iface1=iface1, iface2=iface2)

    # start session
    core.start_session(session=session)

if __name__ == "__main__":
    main()
