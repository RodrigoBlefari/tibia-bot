import time
from image_match import locate_on_window, click_in_window
import keyboard

WINDOW_TITLE = "Dj Random"  # troque se o nome da janela for diferente

IMAGES = {
    "battleoff": "images/battleoff.png",
    "dwarf": "images/dwarf.png",
    "dwarf_hover": "images/dwarf2.png",
    "dwarf_active": "images/dwarf3.png",
    "direita": "images/direita.png",
    "esquerda": "images/esquerda.png"
}

bot_running = True
last_direction = "left"
battleoff_start_time = None

def log(msg):
    print(f"[BOT {time.strftime('%H:%M:%S')}] {msg}")

def toggle_bot():
    global bot_running
    bot_running = not bot_running
    state = "ATIVO" if bot_running else "PAUSADO"
    log(f"BOT {state} (Alt+B para alternar)")

keyboard.add_hotkey('alt+b', toggle_bot)

def locate_and_click(image_key, center_offset=(0, 0), threshold=0.75):
    match, hwnd = locate_on_window(WINDOW_TITLE, IMAGES[image_key], threshold)
    if match:
        x, y, w, h = match
        click_x = x + w // 2 + center_offset[0]
        click_y = y + h // 2 + center_offset[1]
        click_in_window(hwnd, click_x, click_y)
        log(f"Clique em '{image_key}' ({click_x}, {click_y})")
        return True
    return False

def try_combat_mode():
    if locate_on_window(WINDOW_TITLE, IMAGES["dwarf_active"], 1)[0]:
        return True

    if locate_and_click("dwarf", (0, 10), 0.7):
        time.sleep(0.5)
        if locate_and_click("dwarf_hover", (0, 10), 0.7):
            time.sleep(0.5)
        return True
    return False

def move_direction(direction):
    image_key = "direita" if direction == "right" else "esquerda"
    for _ in range(3):
        if locate_and_click(image_key, (0, 0), 0.9):
            return True
        time.sleep(0.5)
    return False

def handle_battle_off():
    global battleoff_start_time, last_direction

    found, _ = locate_on_window(WINDOW_TITLE, IMAGES["battleoff"], 0.75)
    if not found:
        battleoff_start_time = None
        return

    if not battleoff_start_time:
        battleoff_start_time = time.time()
        log("Battle Off detectado. Iniciando contador...")

    elapsed = time.time() - battleoff_start_time
    log(f"Battle Off há {int(elapsed)}s")

    if elapsed >= 30:
        last_direction = "left" if last_direction == "right" else "right"
        battleoff_start_time = time.time()
        log(f"Trocando direção para: {last_direction.upper()}")

    if not move_direction(last_direction):
        alt = "left" if last_direction == "right" else "right"
        move_direction(alt)

def main_loop():
    log("Bot iniciado. Pressione Alt+B para ligar/desligar.")
    while True:
        if bot_running:
            try:
                if not try_combat_mode():
                    handle_battle_off()
            except Exception as e:
                log(f"[ERRO LOOP] {e}")
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
