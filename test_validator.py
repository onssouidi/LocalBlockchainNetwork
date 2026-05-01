from Block import Block
from Blockchain import Blockchain
from pow import proof_of_work
from validator import is_chain_valid, tamper_block

bc = Blockchain(difficulty=1000)

for i in range(1, 4):
    block = Block(
        index         = len(bc.chain),
        data          = [{"sender": "Alice", "receiver": "Bob", "amount": i * 10}],
        previous_hash = bc.get_last_block().hash,
        difficulty    = bc.difficulty
    )
    mined, _ = proof_of_work(block, difficulty=bc.difficulty)
    bc.add_block(mined)

valid, message = is_chain_valid(bc)
print(f"\nTest 1 — Chaîne intacte    :", message)

tamper_block(bc, 3, [{"sender": "Hacker", "receiver": "Hacker", "amount": 9999}])
valid, message = is_chain_valid(bc)
print(f"Test 2 — Après altération  : ",message)