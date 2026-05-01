from pow import MAX_TARGET

def is_chain_valid(blockchain):
    chain = blockchain.chain

    for i in range(1, len(chain)):
        current  = chain[i]
        previous = chain[i - 1]

        if current.hash != current.compute_hash():
            return False, f" Bloc #{i} — hash corrompu"

        if current.previous_hash != previous.hash:
            return False, f" Bloc #{i} — non lié au bloc #{i-1}"

        target = MAX_TARGET // current.difficulty
        if int(current.hash, 16) >= target:
            return False, f" Bloc #{i} — hash ne respecte pas la target PoW"

    return True, f" Chaîne valide — {len(chain)} blocs vérifiés"


def tamper_block(blockchain, block_index, new_data):
    blockchain.chain[block_index].data = new_data
    print(f" Bloc #{block_index} altéré, 51 attack detected  !")