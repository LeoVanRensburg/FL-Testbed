import re

def modify_start_sh():
    file_path = '/home/whoami/Documents/DistributedConsensusAlgorithm/start.sh'
    variable_name = 'TOPOLOGY_CHOICE'
    new_value = '2'

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
        Position(x=405.56219482421875, y=167.58493041992188),
        Position(x=490.94384765625, y=209.94740295410156),
        Position(x=533.992919921875, y=298.0191955566406),
        Position(x=490.94384765625, y=383.4833068847656),
        Position(x=405.4868469238281, y=424.8914794921875),
    ]

    nodes = []
    for node_id, position in enumerate(node_positions, start=1):
        node = session.add_node(_id=node_id, name=str(node_id), position=position)
        node.services.add("Distributed Consensus Algorithm")
        node.services.add("Node Startup Script")
        nodes.append(node)

    # create switch
    switch_position = Position(x=405.2189025878906, y=297.8265686035156)
    switch_node = session.add_node(_id=7, name="n7", position=switch_position, _type=NodeType.SWITCH)

    # create links
    for node in nodes:
        node_iface = iface_helper.create_iface(node_id=node.id, iface_id=0)
        switch_iface = iface_helper.create_iface(node_id=switch_node.id, iface_id=nodes.index(node))

        node_iface.ip4 = f"10.0.0.{20 + nodes.index(node)}"
        node_iface.ip6 = f"2001::{14 + nodes.index(node):x}"

        session.add_link(node1=node, node2=switch_node, iface1=node_iface, iface2=switch_iface)

    # start session
    core.start_session(session=session)


if __name__ == "__main__":
    main()
