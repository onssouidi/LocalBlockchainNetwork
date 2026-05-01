import time
from Block import Block

MAX_TARGET = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
def proof_of_work(block, difficulty=1000):
    target = MAX_TARGET // difficulty
    block.nonce = 0
    iterations = 0
    start_time = time.time()

    while True:
        block.hash = block.compute_hash()
        iterations += 1

        if int(block.hash, 16) < target:
            break

        block.nonce += 1

    elapsed = time.time() - start_time

    metrics = {
        "iterations":  iterations,
        "elapsed":     round(elapsed, 4),
        "hash_rate":   round(iterations / elapsed, 2) if elapsed > 0 else 0,
        "target":      hex(target),
        "final_hash":  block.hash,
        "nonce":       block.nonce
    }

    return block, metrics

def benchmark(difficulties=[100, 500, 1000, 5000, 10000]):

    dummy = Block(
        index=0,
        data=[],
        previous_hash="0" * 64,
        difficulty=1   
    )

    print(f"\n{'='*65}")
    print(f"  {'Difficulty':<14} {'Iterations':<14} {'Time (s)':<14} {'Hash Rate'}")
    print(f"{'='*65}")

    for d in difficulties:
        dummy.nonce = 0
        dummy.difficulty = d
        _, metrics = proof_of_work(dummy, difficulty=d)

        print(
            f"  {d:<14} "
            f"{metrics['iterations']:<14} "
            f"{metrics['elapsed']:<14} "
            f"{metrics['hash_rate']} H/s"
        )

    print(f"{'='*65}\n")