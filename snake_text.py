"""
Snake (Jogo da Cobrinha) em modo texto (terminal) usando curses (só funciona no Linux ou no MacOS).
- Sem classes (sem POO). Estilo puramente funcional, organizado em funções.
- Um único arquivo .py
- Controles: Setas (↑ ↓ ← →) ou WASD
- P = Pausar/Retomar | Q = Sair
- O jogo ajusta velocidade conforme o tamanho da cobra (score).
Compat: usa apenas caracteres ASCII para evitar erro "byte doesn't fit in chtype" no macOS.
"""
import curses
import random
import time

# ==============================
# Configurações
# ==============================
INITIAL_SPEED = 120  # milissegundos entre frames (menor = mais rápido)
MIN_SPEED = 50       # limite mínimo (mais rápido)
SPEED_STEP = 3       # quanto acelera quando cresce
BORDER_PADDING = 1   # borda interna para desenhar (visual)

# --- Caracteres ASCII para compatibilidade ampla (macOS ncurses) ---
FOOD_CHAR = "*"       # alimento
SNAKE_HEAD_CHAR = "@" # cabeça da cobra
SNAKE_BODY_CHAR = "o" # corpo da cobra
WALL_CHAR = "#"       # borda do campo

# Direções como vetores (dy, dx)
UP    = (-1, 0)
DOWN  = (1, 0)
LEFT  = (0, -1)
RIGHT = (0, 1)

# ==============================
# Funções utilitárias
# ==============================
def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def random_empty_cell(height, width, snake, padding=BORDER_PADDING):
    """Escolhe uma célula livre (não ocupada pela cobra) dentro da área jogável."""
    cells = []
    for y in range(padding + 1, height - padding - 1):
        for x in range(padding + 1, width - padding - 1):
            if (y, x) not in snake:
                cells.append((y, x))
    if not cells:
        return None
    return random.choice(cells)

def opposite_dir(d1, d2):
    """Retorna True se d1 e d2 são direções opostas."""
    return d1[0] == -d2[0] and d1[1] == -d2[1]

# ==============================
# Inicialização do terminal
# ==============================
def init_screen():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)  # esconder cursor
    stdscr.keypad(True)
    return stdscr

def end_screen(stdscr):
    curses.nocreak = getattr(curses, "nocbreak", None)
    if curses.nocreak:
        curses.nocreak()
    else:
        curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    try:
        curses.curs_set(1)
    except curses.error:
        pass
    curses.endwin()

# ==============================
# Janela e desenho
# ==============================
def setup_window(stdscr):
    """Configura a janela principal e retorna dimensões."""
    stdscr.clear()
    stdscr.nodelay(True)   # leitura não bloqueante
    try:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # cobra
        curses.init_pair(2, curses.COLOR_RED, -1)     # comida
        curses.init_pair(3, curses.COLOR_CYAN, -1)    # HUD
        curses.init_pair(4, curses.COLOR_WHITE, -1)   # borda
    except curses.error:
        pass

    height, width = stdscr.getmaxyx()
    return height, width

def safe_addstr(stdscr, y, x, s, attr=0):
    """Ignora erros de escrita fora da tela."""
    try:
        stdscr.addstr(y, x, s, attr)
    except curses.error:
        pass
    except OverflowError:
        # Fallback para caractere ASCII simples
        try:
            stdscr.addstr(y, x, s.encode('ascii', 'ignore').decode('ascii') or '#', attr)
        except Exception:
            pass

def safe_addch(stdscr, y, x, ch, attr=0):
    """addch com fallback ASCII para evitar OverflowError em wide chars."""
    try:
        stdscr.addch(y, x, ch, attr)
    except (curses.error, OverflowError, TypeError):
        safe_addstr(stdscr, y, x, (ch if isinstance(ch, str) else str(ch))[:1] or '#', attr)

def draw_border(stdscr, height, width):
    """Desenha borda do campo."""
    y0, y1 = BORDER_PADDING, height - BORDER_PADDING - 1
    x0, x1 = BORDER_PADDING, width - BORDER_PADDING - 1

    for x in range(x0, x1 + 1):
        safe_addch(stdscr, y0, x, WALL_CHAR, curses.color_pair(4))
        safe_addch(stdscr, y1, x, WALL_CHAR, curses.color_pair(4))
    for y in range(y0, y1 + 1):
        safe_addch(stdscr, y, x0, WALL_CHAR, curses.color_pair(4))
        safe_addch(stdscr, y, x1, WALL_CHAR, curses.color_pair(4))

def draw_hud(stdscr, score, speed_ms, paused=False):
    """Mostra placar e instruções no topo."""
    height, width = stdscr.getmaxyx()
    fps = max(1, 1000 // max(1, speed_ms))
    info = f" Score: {score}  Velocidade: {fps}fps  Controles: ←↑↓→/WASD  (P)ausa (Q)uit "
    if paused:
        info += " [PAUSADO] "
    info = info[:max(0, width-2)]
    safe_addstr(stdscr, 0, 1, info, curses.color_pair(3))

def draw_snake_and_food(stdscr, snake, food):
    """Desenha cobra e comida."""
    # comida
    if food:
        y, x = food
        safe_addstr(stdscr, y, x, FOOD_CHAR, curses.color_pair(2))

    # corpo
    for i, (y, x) in enumerate(snake):
        ch = SNAKE_HEAD_CHAR if i == 0 else SNAKE_BODY_CHAR
        safe_addstr(stdscr, y, x, ch, curses.color_pair(1))

# ==============================
# Lógica do jogo
# ==============================
def initial_state(height, width):
    """Cria estado inicial: cobra no centro, comida aleatória, direção para a direita."""
    cy, cx = height // 2, width // 2
    snake = [(cy, cx), (cy, cx-1), (cy, cx-2)]
    direction = RIGHT
    food = random_empty_cell(height, width, snake)
    speed_ms = INITIAL_SPEED
    score = 0
    paused = False
    return snake, direction, food, speed_ms, score, paused

def next_direction(current_dir, key):
    """Converte tecla em nova direção, respeitando regra de não virar 180°."""
    keymap = {
        curses.KEY_UP: UP, curses.KEY_DOWN: DOWN, curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT,
        ord('w'): UP, ord('W'): UP, ord('s'): DOWN, ord('S'): DOWN,
        ord('a'): LEFT, ord('A'): LEFT, ord('d'): RIGHT, ord('D'): RIGHT,
    }
    if key in keymap:
        new_dir = keymap[key]
        if not opposite_dir(current_dir, new_dir):
            return new_dir
    return current_dir

def move_snake(snake, direction):
    """Move a cobra na direção atual, retornando nova lista de segmentos."""
    head_y, head_x = snake[0]
    dy, dx = direction
    new_head = (head_y + dy, head_x + dx)
    new_snake = [new_head] + snake[:-1]
    return new_snake

def grow_snake(snake):
    """Aumenta a cobra mantendo a cauda anterior (cresce 1)."""
    return snake + [snake[-1]]

def hit_wall_or_self(snake, height, width):
    """Detecta colisões com borda ou com o próprio corpo."""
    head = snake[0]
    y, x = head
    # colisão com parede (borda inclusa)
    if y <= BORDER_PADDING or y >= height - BORDER_PADDING - 1:
        return True
    if x <= BORDER_PADDING or x >= width - BORDER_PADDING - 1:
        return True
    # colisão com o corpo
    if head in snake[1:]:
        return True
    return False

def adjust_speed(speed_ms, score):
    """Ajusta velocidade conforme score (quanto maior, mais rápido)."""
    target = INITIAL_SPEED - score * SPEED_STEP
    return clamp(target, MIN_SPEED, INITIAL_SPEED)

def game_step(stdscr, snake, direction, food, speed_ms, score, paused):
    """Executa um passo do jogo. Retorna novo estado e flags."""
    key = stdscr.getch()

    # Comandos de controle
    if key in (ord('q'), ord('Q')):
        return snake, direction, food, speed_ms, score, paused, True, False  # quit
    if key in (ord('p'), ord('P')):
        paused = not paused

    # Atualiza direção se não pausado
    if not paused:
        direction = next_direction(direction, key)

    # Atualiza apenas se não pausado
    if not paused:
        new_snake = move_snake(snake, direction)

        # Comer?
        ate = (food is not None) and (new_snake[0] == food)
        if ate:
            new_snake = grow_snake(new_snake)
            score += 1
            food = random_empty_cell(*stdscr.getmaxyx(), new_snake)
            speed_ms = adjust_speed(speed_ms, score)

        # Checa colisões
        if hit_wall_or_self(new_snake, *stdscr.getmaxyx()):
            return new_snake, direction, food, speed_ms, score, paused, False, True  # game over

        snake = new_snake

    return snake, direction, food, speed_ms, score, paused, False, False

def render(stdscr, snake, food, score, speed_ms, paused):
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    draw_border(stdscr, height, width)
    draw_hud(stdscr, score, speed_ms, paused)
    draw_snake_and_food(stdscr, snake, food)
    stdscr.refresh()

def game_over_screen(stdscr, score):
    height, width = stdscr.getmaxyx()
    msg1 = " GAME OVER "
    msg2 = f" Pontuacao: {score} "
    msg3 = " Pressione R para reiniciar ou Q para sair "
    y = height // 2
    x1 = (width - len(msg1)) // 2
    x2 = (width - len(msg2)) // 2
    x3 = (width - len(msg3)) // 2
    safe_addstr(stdscr, y - 1, x1, msg1, curses.A_BOLD)
    safe_addstr(stdscr, y,     x2, msg2, curses.A_BOLD)
    safe_addstr(stdscr, y + 2, x3, msg3, curses.A_DIM)
    stdscr.refresh()

def wait_restart_or_quit(stdscr):
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return False
        if key in (ord('r'), ord('R')):
            return True

# ==============================
# Loop principal
# ==============================
def game_loop(stdscr):
    height, width = setup_window(stdscr)

    # Área mínima para jogar (evita janelas minúsculas)
    min_h, min_w = 20, 40
    if height < min_h or width < min_w:
        stdscr.clear()
        safe_addstr(stdscr, 1, 1, f"Amplie sua janela do terminal. (mínimo {min_w}x{min_h})")
        safe_addstr(stdscr, 3, 1, "Pressione qualquer tecla para sair...")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        return

    # Estado inicial
    snake, direction, food, speed_ms, score, paused = initial_state(height, width)

    # Tela inicial
    safe_addstr(stdscr, 2, 2, "Jogo da Cobrinha (texto)")
    safe_addstr(stdscr, 4, 2, "Controles: ←↑↓→ ou WASD | (P) Pausa | (Q) Sair")
    safe_addstr(stdscr, 6, 2, "Pressione qualquer tecla para começar...")
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)

    # Loop do jogo
    while True:
        start = time.time()

        # Desenhar
        render(stdscr, snake, food, score, speed_ms, paused)

        # Um passo do jogo
        snake, direction, food, speed_ms, score, paused, want_quit, game_over = game_step(
            stdscr, snake, direction, food, speed_ms, score, paused
        )
        if want_quit:
            break

        if game_over:
            render(stdscr, snake, food, score, speed_ms, paused)
            game_over_screen(stdscr, score)
            if wait_restart_or_quit(stdscr):
                # reinicia estado
                snake, direction, food, speed_ms, score, paused = initial_state(*stdscr.getmaxyx())
                stdscr.nodelay(True)
                continue
            else:
                break

        # Controle de tempo para atingir ~speed_ms por frame
        elapsed_ms = int((time.time() - start) * 1000)
        remaining = speed_ms - elapsed_ms
        if remaining > 0:
            time.sleep(remaining / 1000.0)

def main():
    stdscr = init_screen()
    try:
        game_loop(stdscr)
    finally:
        end_screen(stdscr)

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: main())
