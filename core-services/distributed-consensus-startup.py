from core.services.base import CoreService
from core.services.base import ServiceMode

class NodeStartupScriptService(CoreService):
    # Unique name for your service within CORE
    name: str = "Node Startup Script"
    # The group your service is associated with, used for display in the GUI
    group: str = "Custom Services"
    # List of files associated with the service (none in this case)
    files: list[str] = []
    # Command to be executed at startup
    startup: list[str] = ["/home/leo/Documents/DistributedConsensusAlgorithm/./start.sh"]
    # Set the validation mode to NON_BLOCKING
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING

    def get_text_template(self, name: str) -> str:
        """
        This method could be used to create a log file or additional configuration if needed.
        For now, it logs the node startup.
        """
        return f"""
        echo '${{node.name}} has started.' > {name}_startup.log
        """
