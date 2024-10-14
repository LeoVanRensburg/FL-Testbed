from core.services.base import CoreService

class DistributedConsensusAlgorithmService(CoreService):
    # Unique name for your service within CORE
    name: str = "Distributed Consensus Algorithm"
    # The group your service is associated with, used for display in the GUI
    group: str = "Custom Services"
    # List of files associated with the service (could be scripts or configuration files)
    files: list[str] = []
    # Commands to be executed at startup
    startup: list[str] = [
        "pip3 install phe --no-index --find-links /home/whoami/Documents/DistributedConsensusAlgorithm/setup/phe-1.5.0-py2.py3-none-any.whl"
    ]

    def get_text_template(self, name: str) -> str:
        """
        Returns a script to log the node name or any additional task.
        """
        return f"""
        echo '${{node.name}}' > {name}_log.txt
        """
