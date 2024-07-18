#!/opt/core/venv/bin/python3

import os
from core.api.grpc import client

def get_session_id():
    session_id = os.environ.get("CORE_SESSION_ID")
    
    if not session_id:
        core = client.CoreGrpcClient()
        core.connect()
        try:
            sessions = core.get_sessions()
            if sessions:
                session_id = sessions[0].id
                print(f"Using session ID: {session_id}")
            else:
                print("No active CORE sessions found.")
        finally:
            core.close()
    
    return int(session_id) if session_id else None

def print_network_info(session_id):
    core = client.CoreGrpcClient()
    core.connect()

    try:
        # Get session
        session = core.get_session(session_id)

        # Print session information
        print(f"Session ID: {session.id}")
        print(f"Session State: {session.state}")

        # Get nodes
        print("\nNodes:")
        for node_id in session.nodes:
            node = session.nodes[node_id]
            print(f"  Node ID: {node.id}, Name: {node.name}, Type: {node.type}")

        # Get links
        print("\nLinks:")
        for link in session.links:
            print(f"  Link: Node {link.node1_id} <-> Node {link.node2_id}")
            if hasattr(link, 'interface1') and link.interface1:
                print(f"    Interface 1: {link.interface1.id}")
            if hasattr(link, 'interface2') and link.interface2:
                print(f"    Interface 2: {link.interface2.id}")
            if hasattr(link, 'options') and link.options:
                print(f"    Bandwidth: {link.options.bandwidth} bps")
                print(f"    Delay: {link.options.delay} us")
                print(f"    Loss: {link.options.loss}%")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        core.close()

if __name__ == "__main__":
    session_id = get_session_id()
    if session_id is not None:
        print_network_info(session_id)
    else:
        print("No active CORE session found. Please start a CORE session first.")
