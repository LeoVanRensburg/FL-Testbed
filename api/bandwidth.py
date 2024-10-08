#!/opt/core/venv/bin/python3

import json
from network_utils import get_session_id, get_core_client, sort_links

def get_bandwidth_info(session_id):
    core = get_core_client()
    core.connect()

    try:
        session = core.get_session(session_id)
        
        links = []
        for link in session.links:
            node1, node2 = int(link.node1_id), int(link.node2_id)
            nodes_connected = f"{min(node1, node2)}-{max(node1, node2)}"
            link_info = {
                "nodes-connected": nodes_connected,
                "bandwidth": link.options.bandwidth if hasattr(link, 'options') else None
            }
            links.append(link_info)

        sorted_links = sort_links(links)
        return json.dumps({"bandwidth": sorted_links}, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        core.close()

if __name__ == "__main__":
    session_id = get_session_id()
    if session_id is not None:
        print(get_bandwidth_info(session_id))
    else:
        print(json.dumps({"error": "No active CORE session found. Please start a CORE session first."}))
