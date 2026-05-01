import argparse
import hashlib
import math
import sys
import time

from node import status
import pygame
import requests

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
PANEL_WIDTH = 300
GRID_COLOR = (38, 60, 94)
BACKGROUND_COLOR = (20, 34, 60)
PANEL_COLOR = (219, 120, 24)
PANEL_TEXT = (18, 18, 18)
BLOCK_BORDER = (12, 12, 18)
TEXT_COLOR = (240, 240, 240)
GRID_STEP = 40
BLOCK_SIZE = 70
BLOCK_SPACING = 24
POLL_DELAY = 1.0

COLOR_CACHE = {}


def miner_color(miner_id):
    if miner_id is None:
        miner_id = "GENESIS"

    if miner_id in COLOR_CACHE:
        return COLOR_CACHE[miner_id]

    digest = hashlib.sha256(miner_id.encode("utf-8")).digest()
    r = int(40 + (digest[0] / 255) * 175)
    g = int(40 + (digest[1] / 255) * 175)
    b = int(40 + (digest[2] / 255) * 175)
    COLOR_CACHE[miner_id] = (r, g, b)
    return COLOR_CACHE[miner_id]


def fetch_blockchain(api_url):
    try:
        response = requests.get(f"{api_url}/getblockchain", timeout=4)
        response.raise_for_status()
        payload = response.json()
        return payload.get("chain", [])
    except requests.RequestException:
        return None
def fetch_status(api_url):
    try:
        response = requests.get(f"{api_url}/", timeout=4)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}

def draw_text(surface, text, font, color, x, y):
    for line in text.split("\n"):
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y))
        y += rendered.get_height() + 6


def draw_grid(surface):
    for x in range(0, WINDOW_WIDTH - PANEL_WIDTH, GRID_STEP):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_STEP):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH - PANEL_WIDTH, y), 1)


def compute_stats(chain, node_id):
    if not chain:
        return 0, "N/A"

    miner_counts = {}
    for block in chain:
        miner = block.get("miner") or "GENESIS"
        miner_counts[miner] = miner_counts.get(miner, 0) + 1

    node_blocks = miner_counts.get(node_id, 0)
    best_miner = max(miner_counts.items(), key=lambda item: item[1])[0]
    ratio = round(100 * node_blocks / len(chain), 2)
    best_ratio = round(100 * miner_counts[best_miner] / len(chain), 2)
    return ratio, f"{best_ratio}% ({best_miner})"


def render(screen, font_small, font_large, chain, api_url, node_id):
    screen.fill(BACKGROUND_COLOR)
    draw_grid(screen)

    if chain is None:
        draw_text(
            screen,
            "Impossible de récupérer la blockchain. Vérifiez que le noeud est démarré.",
            font_small,
            (235, 120, 120),
            20,
            20,
        )
        pygame.display.flip()
        return

    draw_text(screen, "BLOCKCHAIN GRAPH", font_large, TEXT_COLOR, 24, 20)
    draw_text(screen, f"Noeud: {node_id}", font_small, TEXT_COLOR, 24, 60)
    draw_text(screen, f"Blocs: {len(chain)}", font_small, TEXT_COLOR, 24, 84)

    stage_width = WINDOW_WIDTH - PANEL_WIDTH
    center_x = stage_width // 2
    top_margin = 140
    max_display = len(chain)

    positions = []
    for index in range(max_display):
        y = top_margin + index * (BLOCK_SIZE + BLOCK_SPACING)
        x = center_x - BLOCK_SIZE // 2 + ((index % 2) * 120 - 60)
        positions.append((x, y))

    for i, block in enumerate(chain):
        if i == 0:
            continue
        start = (positions[i - 1][0] + BLOCK_SIZE // 2, positions[i - 1][1] + BLOCK_SIZE)
        end = (positions[i][0] + BLOCK_SIZE // 2, positions[i][1])
        pygame.draw.line(screen, TEXT_COLOR, start, end, 3)

    for i, block in enumerate(chain):
        x, y = positions[i]
        fill = miner_color(block.get("miner"))
        pygame.draw.rect(screen, fill, (x, y, BLOCK_SIZE, BLOCK_SIZE), border_radius=12)
        pygame.draw.rect(screen, BLOCK_BORDER, (x, y, BLOCK_SIZE, BLOCK_SIZE), width=4, border_radius=12)

        index_text = font_small.render(str(block.get("index")), True, TEXT_COLOR)
        text_rect = index_text.get_rect(center=(x + BLOCK_SIZE / 2, y + BLOCK_SIZE / 2))
        screen.blit(index_text, text_rect)

    active_ratio, best_ratio = compute_stats(chain, node_id)

    panel_x = WINDOW_WIDTH - PANEL_WIDTH
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, 0, PANEL_WIDTH, WINDOW_HEIGHT))
    draw_text(screen, "BLOCK HEIGHT:", font_small, PANEL_TEXT, panel_x + 24, 30)
    draw_text(screen, str(len(chain) - 1), font_large, PANEL_TEXT, panel_x + 24, 70)
    draw_text(screen, "THIS NODE'S MINING RATE:", font_small, PANEL_TEXT, panel_x + 24, 170)
    draw_text(screen, f"{active_ratio}%", font_large, PANEL_TEXT, panel_x + 24, 210)
    draw_text(screen, "BEST PERFORMING NODE'S RATE:", font_small, PANEL_TEXT, panel_x + 24, 320)
    draw_text(screen, best_ratio, font_large, PANEL_TEXT, panel_x + 24, 360)

    pygame.display.flip()


def main():
    parser = argparse.ArgumentParser(description="Visualisation Pygame de la blockchain par mineur")
    parser.add_argument("--api", "-a", type=str, default="http://localhost:5000", help="URL du noeud à interroger")
    parser.add_argument("--node-id", type=str, default=None, help="Identifiant du noeud utilisé pour le calcul du taux de minage")
    args = parser.parse_args()
    api_url = args.api.rstrip("/")
    status = fetch_status(api_url)
    node_id = args.node_id or status.get("node_id") or "UNKNOWN"

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Blockchain Miner Visualization")
    font_small = pygame.font.SysFont("consolas", 18)
    font_large = pygame.font.SysFont("consolas", 36)

    clock = pygame.time.Clock()
    chain = fetch_blockchain(api_url)
    last_poll = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = time.time()
        if current_time - last_poll > POLL_DELAY:
            chain = fetch_blockchain(api_url)
            last_poll = current_time

        render(screen, font_small, font_large, chain, api_url, node_id)
        clock.tick(30)


if __name__ == "__main__":
    main()
