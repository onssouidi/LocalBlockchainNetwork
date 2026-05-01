import hashlib
import json
import time

class Block:
    def __init__(self, index, data, previous_hash, difficulty, nonce=0, miner=None):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.difficulty = difficulty #bech nsettiw el diffculty baed 
        self.nonce = nonce
        self.miner = miner
        self.hash = self.compute_hash()           # ki tetlanca nhotou fih awel hash
    
    def compute_hash(self):
        block_dict = {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "difficulty":    self.difficulty,
            "nonce":         self.nonce,
            "miner":         self.miner
        }
        block_string = json.dumps(block_dict, sort_keys=True) #bech matkounech reordonner baed 
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "difficulty":    self.difficulty,
            "nonce":         self.nonce,
            "hash":          self.hash,
            "miner":         self.miner
        }

    @classmethod
    def from_dict(cls, d):
        block = cls(
            index         = d["index"],
            data          = d["data"],
            previous_hash = d["previous_hash"],
            difficulty    = d["difficulty"],
            nonce         = d["nonce"],
            miner         = d.get("miner")
        )
        block.timestamp = d["timestamp"]
        block.hash      = d["hash"]
        return block