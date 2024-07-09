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

### Basic Usage

Now that everything is successfully installed, you can run core-daemon and core-gui. To run them, use the following commands. 

```
sudop core-daemon
```
and
```
core-gui
```

After having run the following commands, go to the folder in which you cloned the git repo. In that folder, there will be a folder named Scenarios. You can run the python files found within this folder to automatically start and execute a scenario. Alternatively, you can load the XML files within this folder directly through CORE itself. One advantage of using the python files is that you don't need the gui open at all. You can just view the logs. 
For example, if you wanted to run Full-mesh.py, you would need to use the following command:
```
/opt/core/venv/bin/python Full-Mesh.py
```

Alternatively, if you want to open any of the .xml files, you should open the core-gui and go to File -> Open -> the folder where you stored the Scenarios -> Click on the Scenario you want to open -> Open. Then you have to press the start button to start running the scenario. 

### Logging

Then, you can view the logs at:
```
/home/$(whoami)/Documents/logs/
```
Once you get to this folder, you should see more folders labelled 1 through 13. Each of these folders correspond to a node in CORE. Within these folders, you will find a file called log.txt. This folder will contain the full output of each of the nodes. If you run into any errors or want to analyze the results, you will see it in here.

You can also use the log aggregator script to view all the important results. You should launch this script before you start running the scenarios in CORE. It will automatically track the final results and execution times across multiple trials of a given scenario. To use this script you simply have to launch it using python.
```
python3 log-aggregator.py
```
To view the results, you have to press the character q, and then enter. This will stop the script from running and display all the results in the terminal. It's recommended that you stop the script after you change the scenario to something different or change something in the scenario, like the number of transmissions.

### Attacks

To simulate an attack between nodes, you have multiple options. You could simply adjust network links on a certain node to simulate a basic attack such as a DDoS attack. On the other hand, you could also change some of the numbers in the distributed consensus algorithm to simulate a malware attack, where an attacker has taken control of one of your federated learning nodes, and changed the model that is getting sent to mess with your results.

To accomplish the first attack, you need to open up the core-gui. After you have a scenario loaded, you can then simply right click on the red line between 2 nodes. This should pop up a menu where it gives you the option to adjust the bandwidth, latency, jitter, and percent of packets lost. If you give a really low bandwidth limit, and very high latency and packet loss, you would be simulating a basic DDoS attack.

To simulate a malware attack, through a compromised node, you can modify the values that a node sends to other nodes. You can find the files of the distributed consensus algorithm in:
```
/home/$(whoami)/Documents/DistributedConsensusAlgorithm/Algorithm/yourScenariosName/
```
You then have to choose which node is compromised and change the corresponding value in main(nodeName).py. Then you should find the variable titled "nodeValues". After you have found the location of nodeValues, you should change the corresponding value in the array with a different number. This in effect will make this value appear as if a node is compromised and is sending false data to the other nodes. It's also worth noting that you should take note of the original value to see the percentage change. 

## Useful Commands

Some other useful commands are present which can be used to improve the user experience.

The below command allows you to cleanup any remnants of CORE in case of a crash or exit of CORE, so you don't have to manually clean it up.
```
sudop core-cleanup
```
You also have access to the core-cli command. This command can load and modify .xml files. However, it does not appear that you can actually start a session using this command. 
```
sudop core-cli
```

## Youtube Tutorial

Click on the image below to access the video.
[![Video Gif](https://images2.imgbox.com/06/69/mwddjcGF_o.png)](https://www.youtube.com/watch?v=TH2wfQ_YbjA)

## Contact Info
Feel free to send me a email if you have any questions about this project.

Email: research@leeu.me
