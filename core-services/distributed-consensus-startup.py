from typing import Dict, List

from core.config import ConfigString, ConfigBool, Configuration
from core.configservice.base import ConfigService, ConfigServiceMode, ShadowDir


# class that subclasses ConfigService
class DistributedConsensus(ConfigService):
    # unique name for your service within CORE
    name: str = "Distributed Consensus Algorithm"
    # the group your service is associated with, used for display in GUI
    group: str = "Custom Services"
    # directories that the service should shadow mount, hiding the system directory
    directories: List[str] = [
    ]
    # files that this service should generate, defaults to nodes home directory
    # or can provide an absolute path to a mounted directory
    files: List[str] = [
    ]
    # executables that should exist on path, that this service depends on
    executables: List[str] = []
    # other services that this service depends on, can be used to define service start order
    dependencies: List[str] = []
    # commands to run to start this service
    startup: List[str] = [
        "pip3 install phe --no-index --find-links /home/whoami/Documents/DistributedConsensusAlgorithm/setup/phe-1.5.0-py2.py3-none-any.whl",
        "pip3 install paramiko --no-index --find-links /home/whoami/Documents/DistributedConsensusAlgorithm/setup/paramiko-3.4.0-py3-none-any.whl",
    ]
    # commands to run to validate this service
    validate: List[str] = []
    # commands to run to stop this service
    shutdown: List[str] = []
    # validation mode, blocking, non-blocking, and timer
    validation_mode: ConfigServiceMode = ConfigServiceMode.NON_BLOCKING
    # configurable values that this service can use, for file generation
    default_configs: List[Configuration] = [
    ]
    # sets of values to set for the configuration defined above, can be used to
    # provide convenient sets of values to typically use
    modes: Dict[str, Dict[str, str]] = {
    }
    # defines directories that this service can help shadow within a node
    shadow_directories: List[ShadowDir] = [
    ]

    def get_text_template(self, name: str) -> str:
        return """
        # sample script 1
        # node id(${node.id}) name(${node.name})
        # config: ${config}
        echo hello
	    iperf3 -s -p7575 &
        """

