from Blockchain import Blockchain
from transactions import TransactionPool

bc   = Blockchain(difficulty=1000)
pool = TransactionPool()

pool.add_transaction("Alice", "Bob",   50)
pool.add_transaction("Bob",   "Carl",  30)
pool.add_transaction("Carl",  "Alice", 20)
print(pool)

pool.add_transaction("",      "Bob",  10)   
pool.add_transaction("Alice", "Alice", 5)    
pool.add_transaction("Alice", "Bob",  -10)   

pool.mine_pending_transactions(bc)
print(f"\n Chaîne : {len(bc.chain)} blocs")
print(f" Balance Alice : {bc.get_balance('Alice')}")
print(f" Balance Bob   : {bc.get_balance('Bob')}")

pool.mine_pending_transactions(bc)