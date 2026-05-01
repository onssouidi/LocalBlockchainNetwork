from Block import Block

b = Block(
    index=1,
    data=[{"sender": "Alice", "receiver": "Bob", "amount": 50}],
    previous_hash="0" * 64,
    difficulty=1000
)

print(b)
print("Hash valide ?", b.hash == b.compute_hash())
print("to_dict :", b.to_dict())

b2 = Block.from_dict(b.to_dict())
print("from_dict OK ?", b2.hash == b.hash)