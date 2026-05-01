from Block import Block
from Blockchain import Blockchain
from pow import proof_of_work

bc = Blockchain(difficulty=1000)

transactions = [
    [{"sender": "Alice", "receiver": "Bob",   "amount": 50}],
    [{"sender": "Bob",   "receiver": "Carl",  "amount": 30}],
    [{"sender": "Carl",  "receiver": "Alice", "amount": 20}],
]

for txs in transactions:
    block = Block(
        index         = len(bc.chain),
        data          = txs,
        previous_hash = bc.get_last_block().hash,
        difficulty    = bc.difficulty
    )
    mined_block, metrics = proof_of_work(block, difficulty=bc.difficulty)
    bc.add_block(mined_block)
    print(f" Bloc #{mined_block.index} miné en {metrics['elapsed']}s | {metrics['hash_rate']} H/s")

print(bc)

print(f"\n Balance Alice : {bc.get_balance('Alice')}")
print(f" Balance Bob   : {bc.get_balance('Bob')}")
print(f" Balance Carl  : {bc.get_balance('Carl')}")


bc.save()
bc2 = Blockchain()
bc2.load()
print(f"\n Chaîne rechargée : {len(bc2.chain)} blocs")