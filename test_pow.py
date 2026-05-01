from Block import Block
from pow import proof_of_work, benchmark

b = Block(
    index=1,
    data=[{"sender": "Alice", "receiver": "Bob", "amount": 50}],
    previous_hash="0" * 64,
    difficulty=1000
)

mined_block, metrics = proof_of_work(b, difficulty=1000)

print(f"Nonce trouvé   : {metrics['nonce']}")
print(f"Itérations     : {metrics['iterations']}")
print(f"Temps          : {metrics['elapsed']} s")
print(f"Hash rate      : {metrics['hash_rate']} H/s")
print(f"Hash final     : {metrics['final_hash'][:30]}...")
print(f"Target         : {metrics['target'][:20]}...")

# vérifie que le hash respecte bien la target
from pow import MAX_TARGET
target = MAX_TARGET // 1000
assert int(mined_block.hash, 16) < target, "Hash ne respecte pas la target !"
print("\n PoW valide !")

# benchmark
benchmark()