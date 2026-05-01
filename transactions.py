import time
import uuid
from Block import Block
from pow import proof_of_work

class TransactionPool:
    def __init__(self):
        self.pending = []

    def add_transaction(self, sender, receiver, amount):
        if not sender or not receiver:
            print(" Sender ou receiver manquant")
            return False
        if amount <= 0:
            print(" Montant invalide")
            return False
        if sender == receiver:
            print(" Sender et receiver identiques")
            return False

        tx = {
            "id":        str(uuid.uuid4())[:8],   
            "sender":    sender,
            "receiver":  receiver,
            "amount":    amount,
            "timestamp": time.time()
        }

        self.pending.append(tx)
        print(f" Transaction ajoutée : {sender} → {receiver} : {amount}")
        return True


    def get_pending(self):
        return self.pending.copy()

    def size(self):
        return len(self.pending)

   
    def clear(self):
        count = len(self.pending)
        self.pending = []
        print(f" Pool vidé — {count} transactions supprimées")

    def mine_pending_transactions(self, blockchain, miner=None):
        if not self.pending:
            print("  Pool vide — rien à miner")
            return None

        print(f"\n  Minage de {len(self.pending)} transaction(s)...")

        block = Block(
            index         = len(blockchain.chain),
            data          = self.get_pending(),
            previous_hash = blockchain.get_last_block().hash,
            difficulty    = blockchain.difficulty,
            miner         = miner
        )

        mined_block, metrics = proof_of_work(block, difficulty=blockchain.difficulty)
        blockchain.add_block(mined_block)
        self.clear()

        print(
            f" Bloc #{mined_block.index} miné | "
            f"Miner: {mined_block.miner} | "
            f"Nonce: {metrics['nonce']} | "
            f"{metrics['hash_rate']} H/s | "
            f"{metrics['elapsed']}s"
        )

        return mined_block

    def __repr__(self):
        if not self.pending:
            return "📭 Pool vide"
        lines = [f"📬 Pool — {len(self.pending)} transaction(s) en attente :"]
        for tx in self.pending:
            lines.append(
                f"  [{tx['id']}] {tx['sender']} → {tx['receiver']} : {tx['amount']}"
                f" | {tx['timestamp']}"
            )
        return "\n".join(lines)