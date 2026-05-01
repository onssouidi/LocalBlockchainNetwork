# LocalBlockchainNetwork
Test The Blockchain Network with 3 Nodes   
python node.py --port 5000 --node-id Node1 --mine   
python node.py --port 5001 --node-id Node3 --boot-node localhost:5000 --mine  
python node.py --port 5002 --node-id Node2 --boot-node localhost:5000 --mine  
python visualize.py --api http://localhost:5000  
