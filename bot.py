import time
import keyboard
from collections import deque
from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeRemainingColumn, TextColumn
from image_match import locate_on_window, click_in_window

WINDOW_TITLE = "Dj Random"

IMAGES = {
    "battleoff": "images/battleoff.png",
    "dwarf": "images/dwarf.png",
    "dwarf_hover": "images/dwarf2.png",
    "dwarf_active": "images/dwarf3.png",
    "rootworm": "images/rootworm.png",
    "rootworm_hover": "images/rootworm2.png",
    "rootworm_active": "images/rootworm3.png",
    "dwarfGuard": "images/dwarfGuard.png",
    "dwarfGuard_hover": "images/dwarfGuard2.png",
    "dwarfGuard_active": "images/dwarfGuard3.png",
    "dwarfSoldier": "images/dwarfSoldier.png",
    "dwarfSoldier_hover": "images/dwarfSoldier.png",
    "dwarfSoldier_active": "images/dwarfSoldier.png",
    "direita": "images/direita.png",
    "esquerda": "images/esquerda.png"
}

bot_mode_enabled = False
light_spell_enabled = False
light_spell_interval = 30
last_light_time = 0
last_skill_time = 0
skill_interval = 40
last_direction = "left"
battleoff_start_time = None

thoughts = deque(maxlen=3)
logs = deque(maxlen=5)
console = Console()

def update_thought(message):
    thoughts.appendleft(message)

def add_log(msg, level="INFO"):
    emoji = {
        "INFO": "🟢",
        "WARN": "⚠️",
        "ERROR": "❌",
        "ACTION": "✨",
        "STATE": "🔁",
    }.get(level, "ℹ️")
    logs.appendleft(f"{emoji} {msg}")
    if len(msg) < 60:  # Evita quebra de layout por linhas longas
        console.log(f"{emoji} {msg}")

def toggle_bot_mode():
    global bot_mode_enabled
    bot_mode_enabled = not bot_mode_enabled
    state = "Ligado 🟢" if bot_mode_enabled else "Desligado 🔴"
    update_thought(f"[Modo Caçar] {state}")
    add_log(f"Modo Caçar {state}", "STATE")

def toggle_light_mode():
    global light_spell_enabled
    light_spell_enabled = not light_spell_enabled
    state = "Ligada 💡" if light_spell_enabled else "Desligada 🌑"
    update_thought(f"[Luz Automática] {state}")
    add_log(f"Luz Automática {state}", "STATE")

keyboard.add_hotkey('alt+c', toggle_bot_mode)
keyboard.add_hotkey('alt+l', toggle_light_mode)

def locate_and_click(image_key, center_offset=(0, 0), threshold=0.60):
    match, hwnd = locate_on_window(WINDOW_TITLE, IMAGES[image_key], threshold)
    if match:
        x, y, w, h = match
        click_in_window(hwnd, x + w // 2 + center_offset[0], y + h // 2 + center_offset[1])
        update_thought(f"👆 Clicando em '{image_key}'...")
        add_log(f"Clique em '{image_key}'", "ACTION")
        return True
    return False

def try_combat_mode():
    monsters = [
        {"active": "dwarf_active", "idle": "dwarf", "hover": "dwarf_hover"},
        {"active": "rootworm_active", "idle": "rootworm", "hover": "rootworm_hover"},
        {"active": "dwarfGuard_active", "idle": "dwarfGuard", "hover": "dwarfGuard_hover"},
        {"active": "dwarfSoldier_active", "idle": "dwarfSoldier", "hover": "dwarfSoldier_hover"},
    ]

    for monster in monsters:
        if locate_on_window(WINDOW_TITLE, IMAGES[monster["active"]], 1)[0]:
            update_thought("🛡️ Já em combate com um monstro.")
            return True
        if locate_and_click(monster["idle"], (0, 10), 0.7):
            time.sleep(0.5)
            locate_and_click(monster["hover"], (0, 10), 0.7)
            update_thought("⚔️ Iniciando combate com um monstro...")
            return True
    return False

def move_direction(direction):
    image_key = "direita" if direction == "right" else "esquerda"
    update_thought(f"🔄 Movendo para {direction.upper()}...")
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
        update_thought("😴 Sem batalha...")
        add_log("Battle Off detectado. Temporizador iniciado.", "WARN")

    elapsed = time.time() - battleoff_start_time
    if int(elapsed) % 5 == 0:
        add_log(f"Battle Off há {int(elapsed)}s", "WARN")
    if elapsed >= 60:
        last_direction = "left" if last_direction == "right" else "right"
        update_thought(f"➡️ Trocar direção para {last_direction.upper()}")
        battleoff_start_time = time.time()
    if not move_direction(last_direction):
        alt = "left" if last_direction == "right" else "right"
        move_direction(alt)

def auto_cast_light():
    global last_light_time
    keyboard.press_and_release("f4")
    add_log("F4 pressionado para luz mágica!", "ACTION")
    update_thought("💡 Luz mágica ativada!")
    last_light_time = time.time()

def auto_cast_skill():
    global last_skill_time
    keyboard.press_and_release("f12")
    add_log("F12 pressionado para skill especial!", "ACTION")
    update_thought("💥 Skill especial ativada!")
    last_skill_time = time.time()

def get_status_text(counter):
    blink = " " if counter % 2 == 0 else "•"

    bot_color = "green" if bot_mode_enabled else "red"
    light_color = "green" if light_spell_enabled else "red"

    bot_text = Text.assemble(
        ("🟢 " if bot_mode_enabled else "🔴 ", bot_color),
        ("Modo Caçar: ", "bold white"),
        ("Ligado" if bot_mode_enabled else "Desligado", f"bold {bot_color}"),
        f"  {blink}\n"
    )
    light_text = Text.assemble(
        ("💡 " if light_spell_enabled else "🌑 ", light_color),
        ("Luz Automática: ", "bold white"),
        ("Ligada" if light_spell_enabled else "Desligada", f"bold {light_color}"),
        f"  {blink}"
    )
    return Text("🤖 Bot Status\n", style="bold green") + bot_text + light_text

def render_ui(progress_renderable, counter):
    status_text = get_status_text(counter)

    thought_box = Panel(
        Group(status_text, progress_renderable, *[Text(t, style="cyan") for t in thoughts]),
        title="🧠 Pensamentos do Bot",
        border_style="blue",
    )

    log_panel = Panel(
        Group(*[Text(log, style="yellow") for log in logs]),
        title="📜 Logs do Bot",
        border_style="green"
    )

    layout = Layout()
    layout.split_column(
        Layout(thought_box, name="thoughts", size=10),
        Layout(log_panel, name="logs")
    )
    return layout

def main_loop():
    global last_light_time, last_skill_time
    console.clear()
    last_light_time = time.time()
    last_skill_time = time.time()
    blink_counter = 0

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
    )
    light_task = progress.add_task("Próxima luz (F4)", total=light_spell_interval)
    skill_task = progress.add_task("Skill (F12)", total=skill_interval)

    with Live(render_ui(progress, blink_counter), refresh_per_second=4, console=console) as live:
        while True:
            try:
                time.sleep(1)
                blink_counter += 1
                now = time.time()

                elapsed_light = now - last_light_time
                elapsed_skill = now - last_skill_time

                # Luz
                if light_spell_enabled:
                    progress.update(light_task, completed=elapsed_light)
                    if elapsed_light >= light_spell_interval:
                        auto_cast_light()
                        progress.reset(light_task)
                else:
                    progress.reset(light_task, completed=0)

                # Skill
                progress.update(skill_task, completed=elapsed_skill)
                if elapsed_skill >= skill_interval:
                    auto_cast_skill()
                    progress.reset(skill_task)

                if bot_mode_enabled:
                    if not try_combat_mode():
                        handle_battle_off()

                live.update(render_ui(progress, blink_counter))
            except Exception as e:
                add_log(f"Erro: {e}", "ERROR")
                update_thought(f"❌ Erro: {e}")

if __name__ == "__main__":
    main_loop()
