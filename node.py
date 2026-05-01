from flask import Flask, request, jsonify
from Blockchain import Blockchain
from transactions import TransactionPool
from validator import is_chain_valid
from Block import Block
from pow import proof_of_work, MAX_TARGET
import threading
import requests
import argparse
import time

app   = Flask(__name__)


blockchain = Blockchain(difficulty=1000)
pool       = TransactionPool()
peers      = set()
node_id    = None
node_ip    = "localhost"
node_port  = 5000

mining_metrics = {
    "hash_rate":   0.0,
    "iterations":  0,
    "mining":      False,
    "last_block":  0
}


@app.route("/")
def status():
    return jsonify({
        "node_id":      node_id,
        "block_height": len(blockchain.chain),
        "difficulty":   blockchain.difficulty,
        "mempool_size": pool.size(),
        "hash_rate":    mining_metrics["hash_rate"],
        "mining":       mining_metrics["mining"],
        "peers":        list(peers)
    })


@app.route("/addtx")
@app.route("/addtx")
def add_tx():
    sender   = request.args.get("sender")
    receiver = request.args.get("to")
    amount   = request.args.get("amount", type=float)

    if not sender or not receiver:
        return jsonify({
            "success": False,
            "error": "sender and receiver are required"
        }), 400

    if amount is None or amount <= 0:
        return jsonify({
            "success": False,
            "error": "amount is required and must be positive"
        }), 400

    if sender != "GENESIS":
        balance = blockchain.get_balance(sender)
        if balance < amount:
            return jsonify({
                "success": False,
                "error": "insufficient balance",
                "balance": balance
            }), 400

    success = pool.add_transaction(sender, receiver, amount)
    return jsonify({"success": success, "pool_size": pool.size()})

@app.route("/getmempool")
def get_mempool():
    return jsonify(pool.get_pending())


@app.route("/getblockchain")
def get_blockchain():
    return jsonify(blockchain.to_dict())


@app.route("/getlastblock")
def get_last_block():
    return jsonify(blockchain.get_last_block().to_dict())

@app.route("/getbalance")
def get_balance():
    account = request.args.get("account")
    return jsonify({
        "account": account,
        "balance": blockchain.get_balance(account)
    })

@app.route("/addpeer")
def add_peer():
    peer = request.args.get("peer")
    if peer:
        peers.add(peer)
    return jsonify({"peers": list(peers)})

@app.route("/getpeerstore")
def get_peerstore():
    return jsonify(list(peers))

@app.route("/receiveblock", methods=["POST"])
def receive_block():
    data  = request.get_json()
    block = Block.from_dict(data)

    last = blockchain.get_last_block()


    if block.previous_hash != last.hash:
        resolve_conflicts()
        return jsonify({"status": "conflict — resolving"}), 409

    target = MAX_TARGET // block.difficulty
    if int(block.hash, 16) >= target:
        return jsonify({"status": "invalid PoW"}), 400

    blockchain.chain.append(block)
    print(f" Bloc #{block.index} reçu d'un peer")
    return jsonify({"status": "accepted"})

@app.route("/mine")
def mine():
    if pool.size() == 0:
        return jsonify({"status": "pool vide"})
    mined = pool.mine_pending_transactions(blockchain, miner=node_id)
    if mined:
        broadcast_block(mined)
    return jsonify({"status": "ok", "block": mined.to_dict() if mined else None})


@app.route("/resolvesplit")
def resolvesplit():
    replaced = resolve_conflicts()
    return jsonify({
        "status":       "replaced" if replaced else "kept",
        "chain_length": len(blockchain.chain)
    })
    
def broadcast_block(block):
    for peer in peers.copy():
        try:
            requests.post(
                f"http://{peer}/receiveblock",
                json=block.to_dict(),
                timeout=2
            )
            print(f" Bloc #{block.index} diffusé → {peer}")
        except requests.exceptions.RequestException:
            print(f" Peer {peer} injoignable")


def resolve_conflicts():
    global blockchain
    best_length = len(blockchain.chain)
    best_chain  = None

    for peer in peers.copy():
        try:
            r          = requests.get(f"http://{peer}/getblockchain", timeout=2)
            peer_data  = r.json()
            peer_chain = Blockchain.from_dict(peer_data)

            valid, _   = is_chain_valid(peer_chain)
            if valid and len(peer_chain.chain) > best_length:
                best_length = len(peer_chain.chain)
                best_chain  = peer_chain

        except requests.exceptions.RequestException:
            pass

    if best_chain:
        blockchain = best_chain
        print(f" Chaîne remplacée — nouvelle longueur : {best_length}")
        return True

    print(" Notre chaîne est déjà la plus longue")
    return False

def mining_loop():
    print(f" Thread de minage démarré sur {node_id}")

    while True:
        if pool.size() == 0:
            mining_metrics["mining"] = False
            time.sleep(1)
            continue

        mining_metrics["mining"] = True

        block = Block(
            index         = len(blockchain.chain),
            data          = pool.get_pending(),
            previous_hash = blockchain.get_last_block().hash,
            difficulty    = blockchain.difficulty,
            miner         = node_id
        )

        mined_block, metrics = proof_of_work(block, difficulty=blockchain.difficulty)

        mining_metrics["hash_rate"]  = metrics["hash_rate"]
        mining_metrics["iterations"] = metrics["iterations"]
        mining_metrics["last_block"] = mined_block.index

        blockchain.add_block(mined_block)
        pool.clear()
        broadcast_block(mined_block)

        print(
            f"  [{node_id}] Bloc #{mined_block.index} miné | "
            f"{metrics['hash_rate']} H/s | "
            f"Diff: {blockchain.difficulty}"
        )
    
def register_with_boot_node(boot_node):
    try:
        requests.get(
            f"http://{boot_node}/addpeer?peer={node_ip}:{node_port}",
            timeout=2
        )
        peers.add(boot_node)
        r = requests.get(f"http://{boot_node}/getpeerstore", timeout=2)
        for peer in r.json():
            if peer != f"{node_ip}:{node_port}":
                peers.add(peer)

        resolve_conflicts()

        print(f" Connecté au réseau via {boot_node} | Peers: {peers}")

    except requests.exceptions.RequestException:
        print(f"  Boot node {boot_node} injoignable — démarrage solo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",      "-p",  type=int,  default=5000)
    parser.add_argument("--node-id",          type=str,  default=None)
    parser.add_argument("--boot-node",        type=str,  default=None)
    parser.add_argument("--mine",             action="store_true")
    parser.add_argument("--node-ip",          type=str,  default="localhost")
    args = parser.parse_args()

    node_port = args.port
    node_ip   = args.node_ip
    node_id   = args.node_id or f"Node-{args.port}"

    pool.add_transaction("GENESIS", "Alice", 100)
    pool.add_transaction("GENESIS", "Bob",   100)

    if args.boot_node:
        time.sleep(1)  
        register_with_boot_node(args.boot_node)

    if args.mine:
        t = threading.Thread(target=mining_loop, daemon=True)
        t.start()

    print(f" {node_id} démarré sur le port {args.port}")
    app.run(host="0.0.0.0", port=args.port)