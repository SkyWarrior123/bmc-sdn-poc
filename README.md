# BMC-SDN: Blockchain-based Multi-controller Architecture for Secure Software-defined Networks

## Note
- This is an implementaion of the paper BMC-SDN Blockchain-based Multi-controller Architecture for Secure Software-defined Networks which can be accessed https://onlinelibrary.wiley.com/doi/epdf/10.1155/2021/9984666

## Overview
BMC-SDN implements a secure multi-controller Software-Defined Network (SDN) architecture using MultiChain blockchain technology. The system provides robust network management capabilities with distributed control and enhanced security through blockchain consensus.

## Features
- Multi-controller SDN architecture
- Blockchain-based state management
- Real-time flow monitoring and synchronization
- Automated topology management
- Host tracking across controllers
- Consensus-based network state verification
- Logging system for audit trails
- Automatic state recovery and synchronization

## Prerequisites
- Python 3.7+
- MININET
- ONOS Controller
- MultiChain 2.0.2+
- Linux environment

### Required Python Packages
```bash
pip install requests
pip install termcolor
pip install Savoir
pip install logging
```

## Installation

### 1. MININET Setup
Install MININET on your virtual machine or use Docker image of mininet using the command below:
```bash
docker pull iwaseyusuke/mininet
```

and then run the docker container using the command below
```bash 
docker run -it --rm --privileged -e DISPLAY \
             -v /tmp/.X11-unix:/tmp/.X11-unix \
             -v /lib/modules:/lib/modules \
             iwaseyusuke/mininet
```

### 2. ONOS Controller Setup
Configure ONOS with the following specifications:
- Primary Controller IP: 192.168.1.39
- Backup Controller 1 IP: 192.168.1.40
- Backup Controller 2 IP: 192.168.1.41

### 3. MultiChain Installation
Install MultiChain on all three controllers:
```bash
# Login as root
su

# Download and install MultiChain
cd /tmp
wget https://www.multichain.com/download/multichain-2.0.2.tar.gz
tar -xvzf multichain-2.0.2.tar.gz
cd multichain-2.0.2
mv multichaind multichain-cli multichain-util /usr/local/bin
exit
```

### 4. Blockchain Setup
```bash
# Create the blockchain
multichain-util create chain_sdn1

# Initialize blockchain and mine genesis block
multichaind chain_sdn1 -daemon

# Connect to blockchain (on other controllers)
# Replace IP_ADDRESS with the first controller's IP
multichaind chain_sdn1@IP_ADDRESS:6747
```

## Network Configuration

### MININET Custom Topology
Create and run custom topology:
```bash
sudo mn --custom /mininet/custom/newtopo.py --topo mytopo --controller=remote,ip=192.168.1.40
```

### Configure Virtual Switch
Set controllers for each virtual switch:
```bash
sudo ovs-vsctl set-controller s1 tcp:192.168.1.39:6653 tcp:192.168.1.40:6653 tcp:192.168.1.41:6653
```

### Set Controller Roles
In ONOS CLI:
```bash
device-role of:000000000000000c 192.168.1.39 master
```

## Running the Application

1. Update Configuration
   Edit the configuration section in the script:
   ```python
   RPC_USER = 'multichainrpc'
   RPC_PASSWORD = 'your_rpc_password'
   RPC_HOST = '127.0.0.1'
   RPC_PORT = '6746'
   CHAIN_NAME = 'chain_sdn1'
   ```

2. Start the Script
   ```bash
   python3 bmc_sdn.py
   ```

## Monitoring and Logs
- Real-time status updates are displayed in the console with color-coding
- Logs are stored in `activity.log`
- Blockchain state can be monitored using MultiChain CLI tools

## Architecture Details
- Primary Controller (192.168.1.39): Manages flow rules and network state
- Backup Controllers (192.168.1.40, 192.168.1.41): Provide redundancy and consensus
- MultiChain: Ensures secure and distributed state management
- Consensus Mechanism: Validates network state changes across controllers

## Security Features
- Blockchain-based state verification
- Consensus requirements for state changes
- Audit logging of all network changes
- Secure RPC communication
- Multiple controller redundancy

## Best Practices
1. Regular Monitoring:
   - Monitor consensus status
   - Check controller synchronization
   - Review log files

2. Backup and Recovery:
   - Regular blockchain backups
   - Controller configuration backups
   - Document network state

3. Security:
   - Regular password rotation
   - Network isolation
   - Access control implementation

## How to Contribute to repo
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
