# Federated Learning Testbed

**This project uses CORE to develop a Testbed in which researchers and developers can identify and address weaknesses in current and upcoming Federated Learning algorithms before deploying them in the real world.**

### Overview
This project focuses on the development of a testbed for evaluating Federated Learning (FL) under various conditions of unreliable communication, particularly within low-power IoT ecosystems. The testbed will utilize the Common Open Research Emulator (CORE) to simulate heterogeneous physical devices communicating via wireless channels, allowing for the adjustment of network conditions such as bandwidth, latency, jitter, and packet loss. This setup aims to provide a realistic environment for assessing the performance of FL algorithms under conditions that closely mimic real-world scenarios.

### Signifigance
With the increasing adoption of Artificial Intelligence (AI) and Machine Learning (ML), there is a growing need to train ML models efficiently while preserving user privacy. Federated Learning addresses this need by allowing data to remain local to each device during training. However, the unreliable nature of wireless communications poses significant challenges that are not fully understood due to the limitations of current simulation methodologies. This project seeks to bridge that gap by developing a comprehensive testbed that simulates real-world network conditions, providing valuable insights into the impact of network reliability on FL performance.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Contact](#contact)

## Installation

### Recommended Way To Install CORE

Install Ubuntu 22.04 Desktop on either a VPS, Dedicated Server (recommended if GPU required) or VM (recommended if no GPU required).
```
# clone CORE repo
git clone https://github.com/coreemu/core.git
cd core

# install dependencies to run installation task
./setup.sh

# run the following or open a new terminal
source ~/.bashrc
inv install

echo -e "\nexport PATH=\$PATH:/opt/core/venv/bin\nalias sudop='sudo env PATH=\$PATH'" >> ~/.bashrc
```

For good measure, make sure to restart the machine after you have completed the installation process. There appear to be some weird bugs if you don't.

You can now proceed to the Post-install set of instructions.

### Alternative

Before proceeding with the rest of this installation guide, please follow the instructions on [this website](https://coreemu.github.io/core/install.html) to install CORE.

Once you have installed CORE following any of the methods on the website, please proceed to the Post-install set of instructions.

### Post-install

Now you should be able to run core-daemon by running the command:
```
sudop core-daemon
```

If you can successfully run this command, you can proceed below. If not, it is recommended that you follow the install instructions again, and if that fails, consult the CORE documentation. 

Now, go to your Documents folder, or your preferred place and clone this git repo. 
```
git clone https://github.com/LeoVanRensburg/FL-Testbed /home/$(whoami)/Documents/DistributedConsensusAlgorithm
```
Next, we need to rename all the files to have your username for the testbed to function properly. 
```
find /home/$(whoami)/Documents/DistributedConsensusAlgorithm -type f -exec sed -i "s/whoami/$(whoami)/g" {} +
```

Next, we need to move the custom service into the core-daemon so it loads upon startup. This is typically found in /home/$(whoami)/core/daemon/core/configservices/utilservices.
```
cp -r /home/$(whoami)/Documents/DistributedConsensusAlgorithm/core-services/* /home/$(whoami)/core/daemon/core/configservices/utilservices
```

Next, we need to make a directory in which the logs can be made.
```
mkdir -p /home/$(whoami)/Documents/logs/{1..13}
```

We also need to give the script start.sh permissions to execute.
```
chmod +x /home/$(whoami)/Documents/DistributedConsensusAlgorithm/start.sh
```

Now you can proceed to [Usage](#usage).

## Usage

Now that everything is successfully installed, you can run core-daemon and core-gui. To run them, use the following commands. 

```
sudop core-daemon
```
and
```
core-gui
```

After having run the following commands, go to the folder in which you cloned the git repo. In that folder, there will be a folder named Scenarios. Within this folder are XML files which you can load directly from CORE itself. Alternatively, you can run the following python files to automatically start and execute a scenario.

For example, if you wanted to run Full-mesh.py, you would need to use the following command:
```
/opt/core/venv/bin/python Full-Mesh.py
```
## Useful Commands

Some other useful commands are present which can be used to improve the user experience.

The below command allows you to cleanup any remnants of CORE in case of a crash or exit of CORE, so you don't have to manually clean it up.
```
sudop core-cleanup
```

## Youtube Tutorial

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/TH2wfQ_YbjA/0.jpg)](https://www.youtube.com/watch?v=TH2wfQ_YbjA)

## Contact
Email: research@leeu.me
