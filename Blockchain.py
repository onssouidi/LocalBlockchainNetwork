from Block import Block
import json
import time

ADJUSTMENT_INTERVAL = 5     
TARGET_BLOCK_TIME   = 10    

class Blockchain:
    def __init__(self, difficulty=1000):
        self.chain       = []
        self.difficulty  = difficulty
        self.genesis_block = self._create_genesis_block()

    def _create_genesis_block(self):
        initial_funds = [
        {"sender": "GENESIS", "receiver": "Alice", "amount": 100},
        {"sender": "GENESIS", "receiver": "Bob",   "amount": 100},
        {"sender": "GENESIS", "receiver": "Carl",  "amount": 100},
     ]
        genesis = Block(
            index         = 0,
            data          = initial_funds,
            previous_hash = "0" * 64,
            difficulty    = self.difficulty,
            miner         = "GENESIS"
        )
        self.chain.append(genesis)
        return genesis
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, block):
        block.previous_hash = self.get_last_block().hash
        block.hash          = block.compute_hash()
        self.chain.append(block)

        if len(self.chain) % ADJUSTMENT_INTERVAL == 0:
            self._adjust_difficulty()

        return block
    def _adjust_difficulty(self):
        last_block  = self.chain[-1]
        first_block = self.chain[-ADJUSTMENT_INTERVAL]

        actual_time   = last_block.timestamp - first_block.timestamp
        expected_time = TARGET_BLOCK_TIME * ADJUSTMENT_INTERVAL

        if actual_time == 0:
            return

        ratio = actual_time / expected_time

        old_difficulty   = self.difficulty
        new_difficulty   = int(self.difficulty / ratio)

        new_difficulty = max(new_difficulty, self.difficulty // 4)
        new_difficulty = min(new_difficulty, self.difficulty * 4)
        new_difficulty = max(new_difficulty, 1)   

        self.difficulty = new_difficulty

        print(
            f"\n  Ajustement difficulté : {old_difficulty} → {new_difficulty} "
            f"(temps réel: {actual_time:.1f}s, cible: {expected_time}s)"
        )
        
    def get_balance(self, account):
        balance = 0
        for block in self.chain:
            for tx in block.data:
                if tx.get("sender") == account:
                    balance -= tx["amount"]
                if tx.get("receiver") == account:
                    balance += tx["amount"]
        return balance
    
    def to_dict(self):
        return {
            "difficulty": self.difficulty,
            "chain":      [block.to_dict() for block in self.chain]
        }

    @classmethod
    def from_dict(cls, data):
        bc = cls(difficulty=data["difficulty"])
        bc.chain = [Block.from_dict(b) for b in data["chain"]]
        return bc

    def save(self, filename="blockchain.json"):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f" Chaîne sauvegardée dans",filename)

    def load(self, filename="blockchain.json"):
        with open(filename, "r") as f:
            data = json.load(f)
        restored = Blockchain.from_dict(data)
        self.chain      = restored.chain
        self.difficulty = restored.difficulty
        print(f" Chaîne chargée depuis",filename )
        
    def __repr__(self):
        lines = [f"\n{'='*60}", f"  BLOCKCHAIN — {len(self.chain)} blocs | Difficulté: {self.difficulty}", f"{'='*60}"]
        for block in self.chain:
            lines.append(str(block))
        return "\n".join(lines)