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

def get_core_client():
    return client.CoreGrpcClient()

def sort_links(links):
    return sorted(links, key=lambda x: tuple(map(int, x["nodes-connected"].split('-'))))
