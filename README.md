# Local Blockchain Network

A decentralized blockchain network simulator written in Python, implementing Proof-of-Work consensus with dynamic difficulty adjustment. This project demonstrates core blockchain concepts including block creation, transaction management, peer-to-peer networking, and chain validation.

##  Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Components](#components)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Visualization](#visualization)
- [Architecture](#architecture)

##  Overview

This is an educational blockchain implementation that simulates a network of mining nodes. It features:
- **Proof-of-Work mining** with configurable difficulty
- **Dynamic difficulty adjustment** to maintain consistent block time
- **Peer-to-peer networking** with node discovery
- **Transaction mempool** for pending transactions
- **Chain validation** and integrity checking
- **Real-time visualization** of the blockchain network

##  Features

### Core Blockchain Features
- **Block Creation & Hashing**: SHA-256 based block hashing with Merkle tree support
- **Proof-of-Work Mining**: Adjustable difficulty with nonce-based hash computation
- **Difficulty Adjustment**: Automatic difficulty scaling every 5 blocks to target 10-second block time
- **Chain Validation**: Cryptographic verification of block integrity and PoW validity
- **Transaction Pool**: Memory pool for pending transactions before mining

### Network Features
- **Multi-Node Support**: Run multiple independent nodes on different ports
- **Peer Discovery**: Nodes can bootstrap from known peers and discover the network
- **Peer Communication**: Nodes broadcast blocks and transactions to connected peers
- **Mining Metrics**: Track hash rate, iterations, and mining time

### Visualization & Monitoring
- **Real-time Dashboard**: Pygame-based blockchain visualization
- **Block Inspector**: View block details, transactions, and mining information
- **Network Status**: Monitor node health, difficulty, and pool size
- **REST API**: Query blockchain state and submit transactions

##  Project Structure

```
Network/
├── Block.py              # Block class definition and hashing
├── Blockchain.py         # Blockchain management and validation
├── pow.py               # Proof-of-Work algorithm and benchmarking
├── transactions.py      # Transaction pool and transaction management
├── validator.py         # Chain validation and tampering detection
├── node.py             # Flask-based node API and mining logic
├── visualize.py        # Pygame visualization dashboard
├── test_*.py           # Unit and integration tests
└── README.md           # This file
```

## 🔧 Components

### Block.py
Defines the `Block` class representing individual blockchain blocks.

**Key Methods:**
- `compute_hash()`: Generates SHA-256 hash of block data
- `to_dict()`: Serializes block to dictionary format
- `from_dict()`: Deserializes block from dictionary

**Block Structure:**
- `index`: Block position in chain
- `timestamp`: Block creation time
- `data`: Transaction list
- `previous_hash`: Hash of previous block (chain linkage)
- `difficulty`: Mining difficulty level
- `nonce`: Proof-of-Work nonce value
- `miner`: Node ID that mined the block
- `hash`: Block's SHA-256 hash

### Blockchain.py
Manages the complete blockchain state and block addition logic.

**Key Methods:**
- `_create_genesis_block()`: Creates the initial block with distribution of genesis funds
- `add_block()`: Adds a validated block to the chain
- `get_last_block()`: Returns the most recent block
- `_adjust_difficulty()`: Dynamically adjusts difficulty based on block time

**Configuration:**
- `ADJUSTMENT_INTERVAL`: 5 blocks (difficulty adjustment triggers every 5 blocks)
- `TARGET_BLOCK_TIME`: 10 seconds per block

**Genesis Block:** Distributes 100 tokens each to Alice, Bob, and Carl

### pow.py
Implements the Proof-of-Work consensus mechanism.

**Key Functions:**
- `proof_of_work(block, difficulty)`: Mines a block by finding a nonce where hash < target
- `benchmark(difficulties)`: Benchmarks mining performance across difficulty levels

**Algorithm:**
- Iteratively increments nonce
- Computes block hash for each nonce
- Stops when hash is less than the target (computed from difficulty)
- Returns mining metrics (iterations, hash rate, time elapsed)

### transactions.py
Manages the transaction mempool for pending transactions.

**TransactionPool Class Methods:**
- `add_transaction()`: Validates and adds transaction to pool
- `get_pending()`: Returns copy of pending transactions
- `size()`: Returns transaction pool size
- `clear()`: Empties the transaction pool
- `mine_pending_transactions()`: Creates a block from pending transactions

**Transaction Structure:**
- `id`: Unique transaction identifier
- `sender`: Transaction originator
- `receiver`: Transaction recipient
- `amount`: Transaction value
- `timestamp`: Transaction creation time

### validator.py
Validates blockchain integrity and detects tampering.

**Key Functions:**
- `is_chain_valid(blockchain)`: Verifies entire chain integrity
  - Checks hash consistency
  - Verifies block linkage
  - Validates Proof-of-Work on all blocks
- `tamper_block()`: Simulates a 51% attack by modifying block data

### node.py
Flask-based REST API server that implements a blockchain node.

**Key Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Node status (ID, block height, difficulty, peers) |
| `/addtx` | GET | Submit transaction to mempool |
| `/getblockchain` | GET | Retrieve entire blockchain |
| `/mine` | GET | Manually trigger mining |
| `/peer` | POST | Add peer to network |
| `/sync` | GET | Synchronize blockchain with peers |
| `/block/<index>` | GET | Retrieve specific block |
| `/mempool` | GET | View pending transactions |

**Mining Features:**
- Automatic mining thread (when `--mine` flag enabled)
- Configurable mining interval
- Difficulty tracking and adjustment

### visualize.py
Real-time blockchain visualization using Pygame.

**Features:**
- Renders blocks as colored nodes in a grid layout
- Each miner gets a unique color (based on SHA-256 hash)
- Displays block index, hash preview, and transaction count
- Side panel showing:
  - Node information
  - Blockchain statistics
  - Block details on click
  - Transaction list in selected block
- Auto-updates every 1 second from node API

##  Getting Started

### Prerequisites
```bash
python >= 3.8
Flask
pygame
requests
```

### Installation
```bash
# Clone or navigate to the project
cd Network

# Install dependencies
pip install flask pygame requests
```

##  Usage

### Starting the Network

**Terminal 1 - Bootstrap Node (Port 5000):**
```bash
python node.py --port 5000 --node-id Node1 --mine
```

**Terminal 2 - Peer Node (Port 5001):**
```bash
python node.py --port 5001 --node-id Node3 --boot-node localhost:5000 --mine
```

**Terminal 3 - Peer Node (Port 5002):**
```bash
python node.py --port 5002 --node-id Node2 --boot-node localhost:5000 --mine
```

### Visualizing the Blockchain

**Terminal 4 - Launch Visualization:**
```bash
python visualize.py --api http://localhost:5000
```

This opens an interactive Pygame window showing the real-time blockchain state. You can:
- Click on blocks to see transaction details
- Watch as new blocks are mined
- Monitor difficulty changes
- Track all connected nodes

### Submitting Transactions

**Via Browser/curl:**
```bash
curl "http://localhost:5000/addtx?sender=Alice&to=Bob&amount=25"
```

Transactions are automatically added to the mempool and included in the next mined block.

##  API Endpoints

### Node Status
```
GET http://localhost:5000/
```
**Response:**
```json
{
  "node_id": "Node1",
  "block_height": 42,
  "difficulty": 1200,
  "mempool_size": 3,
  "hash_rate": 45000.5,
  "mining": true,
  "peers": ["localhost:5001", "localhost:5002"]
}
```

### Get Blockchain
```
GET http://localhost:5000/getblockchain
```
Returns the complete blockchain with all blocks.

### Add Transaction
```
GET http://localhost:5000/addtx?sender=<SENDER>&to=<RECEIVER>&amount=<AMOUNT>
```

### Manual Mining
```
GET http://localhost:5000/mine
```
Forces the node to mine immediately (if not already mining).

### Get Mempool
```
GET http://localhost:5000/mempool
```
Returns pending transactions awaiting mining.

##  Testing

The project includes comprehensive tests:

- **test_block.py**: Block creation, hashing, and serialization
- **test_blockchain.py**: Blockchain operations and block addition
- **test_pow.py**: Proof-of-Work mining and difficulty verification
- **test_validator.py**: Chain validation and tampering detection
- **test_pool.py**: Transaction pool management

**Run All Tests:**
```bash
python -m pytest
```

**Run Specific Test:**
```bash
python -m pytest test_block.py -v
```

## Visualization Features

The Pygame visualization dashboard displays:

1. **Block Grid**: Each block represented as a colored square
   - Color based on miner's node ID
   - Genesis block is unique
   - Shows block index and hash preview

2. **Side Panel** (Right side of screen):
   - Current node status
   - Block statistics
   - Selected block details
   - Transaction list
   - Mining metrics

3. **Interactions**:
   - Click blocks to view details
   - Auto-refresh every 1 second
   - Scrollable transaction list

##  Architecture

### Network Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Node 1    │◄───►│   Node 2    │◄───►│   Node 3    │
│  Port 5000  │     │  Port 5001  │     │  Port 5002  │
└─────────────┘     └─────────────┘     └─────────────┘
      ▲
      │
      ▼
  Visualization
  (Pygame)
```

### Data Flow
```
User Transaction
    ▼
Transaction Pool (Mempool)
    ▼
Block Mining (PoW)
    ▼
Block Added to Chain
    ▼
Broadcast to Peers
    ▼
Chain Validation
    ▼
Updated Chain State
```

### Difficulty Adjustment Algorithm
- Every 5 blocks, measure actual vs. target time
- If too fast: increase difficulty (make target harder)
- If too slow: decrease difficulty (make target easier)
- Goal: Maintain ~10 second block time

## Security Features

1. **Proof-of-Work**: Prevents spam and secures consensus
2. **Hash Verification**: Ensures block integrity
3. **Chain Validation**: Detects tampering or forks
4. **Nonce**: Proves work was performed for mining difficulty
5. **Immutability**: Changing historical data invalidates entire chain

## Performance Metrics

Mining performance can be benchmarked using:
```python
python -c "from pow import benchmark; benchmark()"
```

This shows iterations, time, and hash rate for various difficulty levels.

## Troubleshooting

### Nodes Not Connecting
- Ensure bootstrap node is running on specified port
- Check firewall settings
- Verify `--boot-node` address is correct

### Mining Too Slow/Fast
- Mining difficulty adjusts automatically
- Check node resources (CPU usage)
- Verify difficulty settings in Blockchain class

### Visualization Not Updating
- Ensure visualization node API is accessible
- Check network connectivity
- Restart visualization if node restarts

## Key Concepts

### Blockchain
A chain of blocks cryptographically linked together, where each block contains:
- Reference to previous block's hash
- Transaction data
- Proof-of-Work evidence
- Timestamp

### Proof-of-Work
Consensus mechanism requiring miners to solve computational puzzles (hash < target), making consensus secure against attacks.

### Difficulty Adjustment
Algorithm that dynamically scales mining difficulty to maintain consistent block creation time despite varying network hash rate.

### Mempool
Collection of valid transactions waiting to be included in a block.

### Fork
When blockchain state diverges; typically resolved by consensus rules (longest chain wins).

##  License

This project is provided for educational purposes.

## Contributing

Contributions welcome! Areas for improvement:
- Implement Merkle trees for transaction verification
- Add wallet and signing functionality
- Implement consensus rules for fork resolution
- Enhance network propagation
- Add transaction fees and rewards

---

**Happy Mining! **  
