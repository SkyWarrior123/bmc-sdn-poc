#!/usr/bin/env python3
"""
BMC-SDN Controller Implementation
--------------------------------
This script implements a Blockchain-based Multi-controller Architecture for Secure Software-defined Networks.
It handles synchronization of flow rules, hosts, and topology information across multiple SDN controllers
using MultiChain blockchain for consensus and security.

Requirements:
- ONOS Controller
- MultiChain
- Python libraries: requests, Savoir, termcolor, logging
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import pprint
import time
import threading
import binascii
import timeit
from termcolor import colored, cprint
from Savoir import Savoir
import logging
from logging.handlers import RotatingFileHandler

# JSON Validation Functions
def is_json(myjson):
    """Validate if a string is valid JSON."""
    try:
        json_object = json.loads(myjson)
        return True
    except ValueError:
        return False

def safe_json(data):
    """Recursively check if a data structure is JSON-safe."""
    if data is None:
        return True
    elif isinstance(data, (bool, int, float)):
        return True
    elif isinstance(data, (tuple, list)):
        return all(safe_json(x) for x in data)
    elif isinstance(data, dict):
        return all(isinstance(k, str) and safe_json(v) for k, v in data.items())
    return False

# Flow Management Functions
def compare_flows(flow1, flow2):
    """Compare two flow configurations, ignoring dynamic fields."""
    if len(flow1["flows"]) != len(flow2["flows"]):
        return "false"
    
    flow11 = flow1.copy()
    flow22 = flow2.copy()
    
    # Remove dynamic fields for comparison
    for flow in flow11["flows"]:
        flow.pop('life', None)
        flow.pop('packets', None)
        flow.pop('bytes', None)
        flow.pop('lastSeen', None)
    
    for flow in flow22["flows"]:
        flow.pop('life', None)
        flow.pop('packets', None)
        flow.pop('bytes', None)
        flow.pop('lastSeen', None)
    
    return "true" if flow11 == flow22 else "false"

def compare_topology(topo1, topo2):
    """Compare two topology configurations, ignoring timestamp."""
    topo11 = topo1.copy()
    topo22 = topo2.copy()
    topo11.pop('time', None)
    topo22.pop('time', None)
    return "true" if topo11 == topo22 else "false"

def pending(flow1):
    """Check if any flows are in pending state."""
    for flow in flow1["flows"]:
        if flow["state"] != "ADDED":
            print(flow["state"] + ' ===> flow still pending')
            return "true"
    return "false"

def stillmac(flow1):
    """Check if flows contain MAC address criteria."""
    for flow in flow1["flows"]:
        for element in flow["selector"]["criteria"]:
            if element["type"] == "ETH_DST":
                print(element["type"] + ' ===> flow stillmac')
                return "true"
    return "false"

# ONOS API Integration Functions
def insert_flows(flow1):
    """Insert flows into ONOS controller."""
    flow11 = flow1.copy()
    for flow in flow11["flows"]:
        # Remove dynamic fields
        for field in ['life', 'packets', 'bytes', 'lastSeen', 'id', 'tableId', 'groupId']:
            flow.pop(field, None)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(
        'http://localhost:8181/onos/v1/flows?appId=org.onosproject.core',
        data=flow11,
        auth=('onos', 'rocks'),
        headers=headers
    )
    print(response.status_code)

def insert_hosts(host1):
    """Insert hosts into ONOS controller."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    for host in host1["hosts"]:
        response = requests.post(
            'http://localhost:8181/onos/v1/hosts',
            data=host,
            auth=('onos', 'rocks'),
            headers=headers
        )
        print(response.status_code)

def insert_topology(topology1):
    """Insert topology into ONOS controller."""
    topology11 = topology1.copy()
    topology11.pop('time', None)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(
        'http://localhost:8181/onos/v1/topology',
        data=topology11,
        auth=('onos', 'rocks'),
        headers=headers
    )
    print(response.status_code)

# Blockchain Integration Functions
def compare_blocks(block1, block2):
    """Compare two blockchain blocks by transaction ID."""
    return 'false' if block1[0]['txid'] != block2[0]['txid'] else 'true'

# Monitoring and Update Threads
def post_flows(current_flow):
    """Monitor and post flow changes to temporary storage."""
    while True:
        get_flows = requests.get(url, auth=('onos', 'rocks'))
        get_flows_json = get_flows.json()
        if compare_flows(current_flow, get_flows_json) == "false":
            current_flow = get_flows_json
            step_f3 = timeit.default_timer()
            with open('data.json', 'w') as json___file:
                json.dump(get_flows_json, json___file)
        time.sleep(0.1)

def post_flows1(current_flow1):
    """Monitor and handle flow changes with consensus."""
    while True:
        with open('data.json') as json_file:
            get_flows_json = json.load(json_file)
        
        if compare_flows(current_flow1, get_flows_json) == "false":
            global step_f1
            step_f1 = timeit.default_timer()
            cprint('change in the flows detected at : ' + str(step_f1), 'white', 'on_grey')
            current_flow1 = get_flows_json
            
            # Wait for pending flows to complete
            while pending(current_flow1) == "true":
                get_flows = requests.get(url, auth=('onos', 'rocks'))
                get_flows_json = get_flows.json()
                current_flow1 = get_flows_json
                time.sleep(1)
            
            # Consensus check
            step_f2 = timeit.default_timer()
            cprint('beginning flow consensus at : ' + str(step_f2-step_f1), 'white', 'on_grey')
            urlbackup = 'http://192.168.1.40:8181/onos/v1/flows'
            get_backup_flows = requests.get(urlbackup, auth=('onos', 'rocks'))
            get_backup_flows_json = get_backup_flows.json()
            
            if compare_flows(current_flow1, get_backup_flows_json) == "false":
                step_ff2 = timeit.default_timer()
                cprint('flows consensus not reached : ' + str(step_ff2-step_f1), 'white', 'on_red')
                logger.warning('flows consensus not reached, consensus level = 0%, senderIp: 192.168.1.39')
            else:
                step_f3 = timeit.default_timer()
                cprint('flows consensus reached at : ' + str(step_f3-step_f2), 'white', 'on_grey')
                api.publish("sdn_flows", "key1", {'json': current_flow1})
                global step_f4
                step_f4 = timeit.default_timer()
                cprint('flows posted to blockchain at : ' + str(step_f4-step_f3), 'white', 'on_grey')
        
        time.sleep(1)

# Logger Configuration
def setup_logger():
    """Configure logging system."""
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    
    # File handler
    file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Main execution
if __name__ == "__main__":
    # Initialize logger
    setup_logger()
    
    # MultiChain configuration
    rpcuser = 'multichainrpc'
    rpcpasswd = 'your_rpc_password' # For ex: 2RPJYthqTCH1S1rz62iLFJb62DEVRiomPy9VKLmeVJVb
    rpchost = '127.0.0.1'
    rpcport = '6746'
    chainname = 'chain_sdn1'
    
    # Initialize MultiChain API
    api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)
    myaddress = 'your_address' # For ex: 1DNTCuJ62djSorwZ5cNE7yku64MZmQJdpsSaTM
    
    # ONOS API endpoints
    url = 'http://192.168.1.39:8181/onos/v1/flows'
    url2 = 'http://192.168.1.39:8181/onos/v1/hosts'
    url3 = 'http://192.168.1.39:8181/onos/v1/topology'
    
    # Initialize current states
    get_flows = requests.get(url, auth=('onos', 'rocks'))
    current_flow = current_flow1 = get_flows.json()
    
    # Start monitoring threads
    threading.Timer(1, post_flows, [current_flow]).start()
    threading.Timer(1, post_flows1, [current_flow1]).start()
    
    print('All processes started at: ' + time.ctime())