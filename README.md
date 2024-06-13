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

# add to ~/.bashrc
export PATH=$PATH:/opt/core/venv/bin

# add an alias to ~/.bashrc or something similar
alias sudop='sudo env PATH=$PATH'
```

For good measure, make sure to restart the machine after you have completed the installation process. There appear to be some weird bugs if you don't.

Now you should be able to run core-daemon by running the command:
```
sudop core-daemon
```

Now, go to your Documents folder, or your preferred place and clone this git repo. 
```
git clone LeoVanRensburg/FL-Testbed
```
Next, we need to move the custom service into the core-daemon so it loads upon startup. This is typically found in /home/$(whoami)/core/daemon/core/configservices/utilservices.
```
cp -r FL-Testbed/core-services /home/$(whoami)/core/daemon/core/configservices/utilservices
```

Next, navigate to your install location, typically found in /home/$(whoami)/core/daemon/core/configservices/utilservices
While in this folder, make copy the files found in this github repo (insert link here) to this folder.

Now you can proceed to [Usage](#usage).

### Alternative
Before proceeding with the rest of this installation guide, please follow the instructions on [this website](https://coreemu.github.io/core/install.html) to install CORE.

### Post-install

Once you have completed the installation and verified CORE is working, you can continue with the following steps:
1. Clone the github repo
2. Move the files to X

## Usage
```
# now you can run commands like so
sudop core-daemon
```
and
```
core-gui
```

Run the scripts to navigate through the provided scenarios.

## Contact
Email: research@leeu.me
