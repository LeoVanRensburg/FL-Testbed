#!/opt/core/venv/bin/python3

import os
import json
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
            else:
                return None
        finally:
            core.close()
    
    return int(session_id) if session_id else None

def get_network_info(session_id):
    core = client.CoreGrpcClient()
    core.connect()

    try:
        session = core.get_session(session_id)
        
        result = {
            "session_id": session.id,
            "session_state": str(session.state),
            "nodes": [],
            "links": []
        }

        for node_id in session.nodes:
            node = session.nodes[node_id]
            result["nodes"].append({
                "id": node.id,
                "name": node.name,
                "type": str(node.type)
            })

        links = []
        for link in session.links:
            node1, node2 = int(link.node1_id), int(link.node2_id)
            nodes_connected = f"{min(node1, node2)}-{max(node1, node2)}"
            link_info = {
                "nodes-connected": nodes_connected
            }
            if hasattr(link, 'interface1') and link.interface1:
                link_info["interface1"] = link.interface1.id
            if hasattr(link, 'interface2') and link.interface2:
                link_info["interface2"] = link.interface2.id
            if hasattr(link, 'options') and link.options:
                link_info["bandwidth"] = link.options.bandwidth
                link_info["delay"] = link.options.delay
                link_info["loss"] = link.options.loss
            links.append(link_info)

        # Sort links based on the "nodes-connected" field
        sorted_links = sorted(links, key=lambda x: tuple(map(int, x["nodes-connected"].split('-'))))
        result["links"] = sorted_links

        return json.dumps(result, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        core.close()

if __name__ == "__main__":
    session_id = get_session_id()
    if session_id is not None:
        print(get_network_info(session_id))
    else:
        print(json.dumps({"error": "No active CORE session found. Please start a CORE session first."}))
