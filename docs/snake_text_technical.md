# Documentação Técnica - Snake Text (`snake_text.py`)

## 1. Visão Geral

**Jogo da Cobrinha** implementado em Python usando a biblioteca `curses` para renderização no terminal. Arquitetura puramente funcional (sem classes), organizada em funções modulares.

**Características:**
- Apenas caracteres ASCII (compatível com macOS/Linux)
- Controles: Setas ou WASD
- Velocidade adaptativa (acelera conforme pontuação)
- Estados: RUNNING, PAUSED, GAME_OVER


## 2. Arquitetura do Código

```
┌──────────────────────────────────────────────────────────────┐
│                     ESTRUTURA DO MÓDULO                      │
├──────────────────────────────────────────────────────────────┤
│  1. Configurações e Constantes (linhas 14-32)                │
│  2. Funções Utilitárias (linhas 37-53)                       │
│  3. Inicialização do Terminal (linhas 58-78)                 │
│  4. Janela e Desenho (linhas 83-153)                         │
│  5. Lógica do Jogo (linhas 157-244)                          │
│  6. Renderização e Game Over (linhas 247-276)                │
│  7. Loop Principal (linhas 280-336)                          │
│  8. Entry Point (linhas 337-345)                             │
└──────────────────────────────────────────────────────────────┘
```


## 3. Constantes e Configurações

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `INITIAL_SPEED` | `120` | Velocidade inicial em ms por frame |
| `MIN_SPEED` | `50` | Velocidade mínima (limite de aceleração) |
| `SPEED_STEP` | `3` | Redução de ms por ponto scored |
| `BORDER_PADDING` | `1` | Margem visual para a borda |
| `FOOD_CHAR` | `"*"` | Caractere da comida |
| `SNAKE_HEAD_CHAR` | `"@"` | Caractere da cabeça |
| `SNAKE_BODY_CHAR` | `"o"` | Caractere do corpo |
| `WALL_CHAR` | `"#"` | Caractere da parede |

**Direções como vetores (dy, dx):**
```python
UP    = (-1, 0)   # linha -1
DOWN  = (1, 0)    # linha +1
LEFT  = (0, -1)   # coluna -1
RIGHT = (0, 1)    # coluna +1
```


## 4. Estruturas de Dados

### 4.1 Estado do Jogo (tupla retornada por `initial_state`)

```python
snake      # List[Tuple[int, int]] - Lista de posições (y, x)
direction  # Tuple[int, int] - Direção atual (vetor)
food       # Tuple[int, int] | None - Posição da comida
speed_ms   # int - Milissegundos entre frames
score      # int - Pontuação atual
paused     # bool - Estado de pausa
```

### 4.2 Exemplo de Estado Inicial

```python
snake = [(12, 20), (12, 19), (12, 18)]  # 3 segmentos no centro
direction = (0, 1)                        # movendo para direita
food = (15, 25)                          # comida em posição aleatória
speed_ms = 120
score = 0
paused = False
```


## 5. Funções Detalhadas

### 5.1 Utilitárias

#### `clamp(n, lo, hi)`
Limita um valor dentro de um intervalo.

```python
def clamp(n, lo, hi):
    return max(lo, min(hi, n))
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `n` | int | Valor a ser limitado |
| `lo` | int | Limite inferior |
| `hi` | int | Limite superior |

**Complexidade:** O(1)


#### `random_empty_cell(height, width, snake, padding)`
Retorna uma posição aleatória livre (não ocupada pela cobra).

```python
def random_empty_cell(height, width, snake, padding=BORDER_PADDING):
    cells = []
    for y in range(padding + 1, height - padding - 1):
        for x in range(padding + 1, width - padding - 1):
            if (y, x) not in snake:
                cells.append((y, x))
    return random.choice(cells) if cells else None
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `height` | int | Altura do terminal |
| `width` | int | Largura do terminal |
| `snake` | List[Tuple] | Lista de posições ocupadas |
| `padding` | int | Margem de borda |

**Complexidade:** O(H × W) onde H=altura, W=largura


#### `opposite_dir(d1, d2)`
Verifica se duas direções são opostas (evita voltar 180°).

```python
def opposite_dir(d1, d2):
    return d1[0] == -d2[0] and d1[1] == -d2[1]
```

**Exemplos:**
```python
opposite_dir(UP, DOWN)    # True
opposite_dir(LEFT, RIGHT) # True
opposite_dir(UP, LEFT)    # False
```


### 5.2 Terminal

#### `init_screen()`
Configura o terminal para curses (sem eco, cbreak, cursor escondido).

```python
def init_screen():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)
    return stdscr
```

**Efeitos colaterais:**
- Desabilita eco de caracteres
- Desabilita line buffering
- Esconde o cursor
- Habilita keypad para setas


#### `end_screen(stdscr)`
Restaura o terminal ao estado original.

```python
def end_screen(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()
```

**Importância:** Sempre deve ser chamada, mesmo se ocorrer erro.


### 5.3 Desenho

#### `setup_window(stdscr)`
Configura cores e retorna dimensões do terminal.

```python
def setup_window(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)  # Leitura não bloqueante
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Cobra
    curses.init_pair(2, curses.COLOR_RED, -1)     # Comida
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # HUD
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # Borda
    return stdscr.getmaxyx()
```

**Cores disponíveis:**
| Par | Cor | Uso |
|-----|-----|-----|
| 1 | Verde | Cobra |
| 2 | Vermelho | Comida |
| 3 | Ciano | HUD |
| 4 | Branco | Borda |


#### `safe_addstr(stdscr, y, x, s, attr)`
Escreve string na tela com tratamento de erros.

```python
def safe_addstr(stdscr, y, x, s, attr=0):
    try:
        stdscr.addstr(y, x, s, attr)
    except curses.error:
        pass
    except OverflowError:
        # Fallback ASCII para macOS
        try:
            stdscr.addstr(y, x, s.encode('ascii', 'ignore').decode('ascii') or '#', attr)
        except Exception:
            pass
```

**Por que `safe_addstr`?**
- Evita crash se coordenadas forem inválidas
- Fallback para ASCII no macOS (que tem problema com caracteres unicode)


#### `draw_border(stdscr, height, width)`
Desenha a borda do campo de jogo.

```
######################  ← borda superior
#                    #
#                    #
#                    #
######################  ← borda inferior
```


#### `draw_hud(stdscr, score, speed_ms, paused)`
Desenha o HUD no topo da tela.

```
 Score: 5  Velocidade: 13fps  Controles: ←↑↓→/WASD  (P)ausa (Q)uit [PAUSADO]
```


### 5.4 Lógica do Jogo

#### `initial_state(height, width)`
Cria o estado inicial do jogo.

```python
def initial_state(height, width):
    cy, cx = height // 2, width // 2
    snake = [(cy, cx), (cy, cx-1), (cy, cx-2)]  # 3 segmentos
    direction = RIGHT
    food = random_empty_cell(height, width, snake)
    speed_ms = INITIAL_SPEED
    score = 0
    paused = False
    return snake, direction, food, speed_ms, score, paused
```

**Posicionamento inicial:**
```
# Campo 40x20 (exemplo)
     0         1         2         3
     0123456789012345678901234567890123456789
  0  ########################################
  .  #                                      #
  .  #          @ o o *                     #  ← cobra começa no centro
  .  #                                      #
 19  ########################################
```



#### `next_direction(current_dir, key)`
Converte tecla pressionada em nova direção.

```python
def next_direction(current_dir, key):
    keymap = {
        curses.KEY_UP: UP, curses.KEY_DOWN: DOWN,
        curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT,
        ord('w'): UP, ord('W'): UP, ord('s'): DOWN, ord('S'): DOWN,
        ord('a'): LEFT, ord('A'): LEFT, ord('d'): RIGHT, ord('D'): RIGHT,
    }
    if key in keymap:
        new_dir = keymap[key]
        if not opposite_dir(current_dir, new_dir):
            return new_dir
    return current_dir
```

**Mapa de teclas:**
| Tecla | Direção |
|-------|---------|
| ↑ / w / W | UP |
| ↓ / s / S | DOWN |
| ← / a / A | LEFT |
| → / d / D | RIGHT |


#### `move_snake(snake, direction)`
Move a cobra uma posição na direção atual.

```python
def move_snake(snake, direction):
    head_y, head_x = snake[0]
    dy, dx = direction
    new_head = (head_y + dy, head_x + dx)  # Nova posição da cabeça
    new_snake = [new_head] + snake[:-1]    # Adiciona cabeça, remove cauda
    return new_snake
```

**Diagrama do movimento:**
```
Antes:        Depois (direção RIGHT):
[@, o, o]     [*, @, o]
  ↑             
nova cabeça   corpo anterior vira cabeça
```

**Complexidade:** O(n) onde n = tamanho da cobra


#### `grow_snake(snake)`
Aumenta a cobra em 1 segmento (não remove a cauda).

```python
def grow_snake(snake):
    return snake + [snake[-1]]  # Adiciona cópia da cauda
```

**Diagrama:**
```
Antes: [@, o, o]
Depois: [@, o, o, o]  ← última posição duplicada
```


#### `hit_wall_or_self(snake, height, width)`
Detecta colisão com parede ou corpo.

```python
def hit_wall_or_self(snake, height, width):
    head = snake[0]
    y, x = head
    
    # Colisão com borda
    if y <= BORDER_PADDING or y >= height - BORDER_PADDING - 1:
        return True
    if x <= BORDER_PADDING or x >= width - BORDER_PADDING - 1:
        return True
    
    # Colisão com corpo
    if head in snake[1:]:
        return True
    
    return False
```

**Complexidade:** O(n) para checagem de colisão com corpo


#### `adjust_speed(speed_ms, score)`
Ajusta velocidade baseado na pontuação.

```python
def adjust_speed(speed_ms, score):
    target = INITIAL_SPEED - score * SPEED_STEP
    return clamp(target, MIN_SPEED, INITIAL_SPEED)
```

**Exemplo de progressão:**
| Score | speed_ms | FPS aproximado |
|-------|----------|---------------|
| 0 | 120 | 8.3 |
| 10 | 90 | 11.1 |
| 20 | 60 | 16.7 |
| 23+ | 50 | 20 (máximo) |


#### `game_step(stdscr, snake, direction, food, speed_ms, score, paused)`
Executa um passo do jogo (input + update).

```python
def game_step(stdscr, snake, direction, food, speed_ms, score, paused):
    key = stdscr.getch()  # Lê tecla (não bloqueante)
    
    # Processa comandos
    if key == ord('q'): return ..., quit=True
    if key == ord('p'): paused = not paused
    
    # Atualiza direção
    if not paused:
        direction = next_direction(direction, key)
    
    # Move cobra
    if not paused:
        new_snake = move_snake(snake, direction)
        
        # Comeu?
        if new_snake[0] == food:
            new_snake = grow_snake(new_snake)
            score += 1
            food = random_empty_cell(...)
            speed_ms = adjust_speed(...)
        
        # Colidiu?
        if hit_wall_or_self(new_snake, ...):
            return ..., game_over=True
        
        snake = new_snake
    
    return snake, direction, food, speed_ms, score, paused, quit, game_over
```


### 5.5 Renderização

#### `render(stdscr, snake, food, score, speed_ms, paused)`
Renderiza o estado completo do jogo.

```python
def render(stdscr, snake, food, score, speed_ms, paused):
    stdscr.erase()                          # Limpa tela
    height, width = stdscr.getmaxyx()
    draw_border(stdscr, height, width)      # Borda
    draw_hud(stdscr, score, speed_ms, paused)  # HUD
    draw_snake_and_food(stdscr, snake, food)   # Cobra e comida
    stdscr.refresh()                       # Atualiza tela física
```


#### `game_over_screen(stdscr, score)`
Mostra tela de game over centralizada.

```
         GAME OVER 
      Pontuacao: 10 
 Pressione R para reiniciar ou Q para sair 
```


### 5.6 Loop Principal

#### `game_loop(stdscr)`
Loop principal do jogo.

```python
def game_loop(stdscr):
    height, width = setup_window(stdscr)
    
    # Verifica tamanho mínimo
    if height < 20 or width < 40:
        # Mostra erro e sai
        return
    
    # Estado inicial
    snake, direction, food, speed_ms, score, paused = initial_state(...)
    
    # Tela inicial (aguarda tecla)
    show_start_screen()
    
    # GAME LOOP
    while True:
        start = time.time()
        
        # 1. Render
        render(stdscr, snake, food, score, speed_ms, paused)
        
        # 2. Game Step (input + update)
        snake, direction, food, speed_ms, score, paused, quit, game_over = game_step(...)
        
        if quit: break
        if game_over:
            show_game_over()
            if restart: continue
            else: break
        
        # 3. Frame rate control
        elapsed = int((time.time() - start) * 1000)
        if speed_ms - elapsed > 0:
            time.sleep((speed_ms - elapsed) / 1000)
```

**Diagrama do loop:**
```
┌──────────────────────────────────────┐
│           GAME LOOP                  │
│                                      │
│  ┌─────────┐   ┌──────────────────┐  │
│  │  start  │   │  render()        │  │
│  └────┬────┘   └────────┬─────────┘  │
│       │                 │            │
│       └────────┬────────┘            │
│            render                    │
│                ↓                     │
│       ┌────────────────┐             │
│       │  game_step()   │             │
│       │  - getch()     │             │
│       │  - move_snake()│             │
│       │  - collision   │             │
│       └───────┬────────┘             │
│               │                      │
│       ┌───────┴───────┐              │
│       ↓               ↓              │
│    QUIT?          GAME_OVER?         │
│       ↓               ↓              │
│     break         tela_game_over     │
│                     ↓                │
│              restart?                │
│               ↓     ↓                │
│            True    False             │
│              ↓       ↓               │
│         continue   break             │
│             └───────┘                │
│                 ↓                    │
│        frame_rate_control()          │
│                 ↓                    │
│            repeat loop               │
└──────────────────────────────────────┘
```


## 6. Fluxo de Execução Completo

```
[main()]
    │
    ├─→ init_screen()
    │       │
    │       └─→ curses.initscr()
    │           curses.noecho()
    │           curses.cbreak()
    │           curses.curs_set(0)
    │
    ├─→ game_loop(stdscr)
    │       │
    │       ├─→ setup_window()
    │       │       │
    │       │       ├─→ start_color()
    │       │       ├─→ init_pair() × 4
    │       │       └─→ return (height, width)
    │       │
    │       ├─→ [Verifica tamanho mínimo]
    │       │
    │       ├─→ initial_state()
    │       │       │
    │       │       ├─→ snake = [(cy,cx), (cy,cx-1), (cy,cx-2)]
    │       │       ├─→ direction = RIGHT
    │       │       ├─→ food = random_empty_cell()
    │       │       └─→ return (snake, direction, food, speed, score, paused)
    │       │
    │       ├─→ [Tela inicial - aguarda tecla]
    │       │
    │       └─→ WHILE (game loop)
    │               │
    │               ├─→ start = time.time()
    │               │
    │               ├─→ render()
    │               │       ├─→ erase()
    │               │       ├─→ draw_border()
    │               │       ├─→ draw_hud()
    │               │       ├─→ draw_snake_and_food()
    │               │       └─→ refresh()
    │               │
    │               ├─→ game_step()
    │               │       ├─→ getch() → key
    │               │       ├─→ [Q?] → quit
    │               │       ├─→ [P?] → toggle paused
    │               │       ├─→ next_direction()
    │               │       ├─→ move_snake()
    │               │       ├─→ [comeu?] → grow_snake()
    │               │       ├─→ hit_wall_or_self()
    │               │       └─→ [game_over?] → return game_over=True
    │               │
    │               ├─→ [quit?] → break
    │               │
    │               ├─→ [game_over?] 
    │               │       ├─→ render()
    │               │       ├─→ game_over_screen()
    │               │       └─→ wait_restart_or_quit()
    │               │
    │               └─→ frame_rate_control()
    │                       └─→ sleep(remaining)
    │
    └─→ end_screen()
            │
            └─→ curses.nocbreak()
                curses.echo()
                curses.curs_set(1)
                curses.endwin()
```


## 7. Tratamento de Erros

### 7.1 Erros Capturados

| Função | Erro | Tratamento |
|--------|------|------------|
| `safe_addstr` | `curses.error` | Ignora silenciosamente |
| `safe_addstr` | `OverflowError` | Fallback para ASCII |
| `safe_addch` | `curses.error`, `OverflowError`, `TypeError` | Usa primeiro caractere |
| `end_screen` | `curses.error` (curs_set) | Ignora |

### 7.2 Por que tratamento de erros?

1. **macOS ncurses** não suporta caracteres unicode
2. **Coordenadas inválidas** podem ocorrer em janelas redimensionadas
3. **Race conditions** raras no terminal


## 8. Complexidade Algorítmica

| Função | Complexidade | Justificativa |
|--------|-------------|---------------|
| `move_snake` | O(n) | Slice list + prepend |
| `grow_snake` | O(1) | Append simples |
| `hit_wall_or_self` | O(n) | `in` em lista |
| `random_empty_cell` | O(H×W) | Itera todo grid |
| `game_step` | O(n) | Dominado por `move_snake`/`hit_wall_or_self` |

Onde n = tamanho da cobra, H = altura, W = largura do terminal.


## 9. Limitações Conhecidas

1. **Não funciona no Windows** (curses é POSIX-only)
2. **Sem persistência** de high score
3. **Sem som**
4. **Sem power-ups**
5. **Tabuleiro fixo** ao tamanho do terminal
6. **Colisão O(n)** poderia ser O(1) com set


## 10. Como Executar

```bash
# Requisito: Python 3 + curses (nativo no Linux/macOS)
python3 snake_text.py
```

**Controles:**
| Tecla | Ação |
|-------|------|
| ↑ ↓ ← → | Mover |
| W A S D | Mover (alternativo) |
| P | Pausar/Retomar |
| Q | Sair |
| R | Reiniciar (após game over) |


## 11. Sugestões de Melhoria

### 11.1 Performance

```python
# Usar set para O(1) em vez de O(n)
def hit_wall_or_self(snake, height, width):
    snake_set = set(snake)
    if head in snake_set:
        return True
    # ...
```

### 11.2 Wrap Around (atravessar paredes)

```python
def move_snake(snake, direction):
    head_y, head_x = snake[0]
    dy, dx = direction
    # Wrap-around usando módulo
    new_y = (head_y + dy) % height
    new_x = (head_x + dx) % width
    new_head = (new_y, new_x)
    new_snake = [new_head] + snake[:-1]
    return new_snake
```

### 11.3 Comida Especial

```python
def game_step(...):
    # ...
    if ate:
        if score % 5 == 0:
            # Comida especial: +3 pontos, não acelera
            score += 3
        else:
            score += 1
            speed_ms = adjust_speed(...)
```

### 11.4 High Score Persistente

```python
import json
from pathlib import Path

HIGH_SCORE_FILE = Path.home() / ".snake_highscore"

def load_high_score():
    if HIGH_SCORE_FILE.exists():
        return int(HIGH_SCORE_FILE.read_text())
    return 0

def save_high_score(score):
    HIGH_SCORE_FILE.write_text(str(score))
```


## 12. Diagrama de Classes de Funções

```
┌─────────────────────────────────────────────────────────────────┐
│                     snake_text.py                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐     ┌──────────────────────────────────┐  │
│  │  CONSTANTES      │     │  UTILITÁRIAS                     │  │
│  │  - INITIAL_SPEED │     │  - clamp()                       │  │
│  │  - MIN_SPEED     │────▶│  - random_empty_cell()           │  │
│  │  - SPEED_STEP    │     │  - opposite_dir()                │  │
│  │  - Direções UP.. │     └──────────────────────────────────┘  │
│  └─────────────────┘                    │                       │
│                                         │                       │
│  ┌─────────────────────────────────────▼──────────────────────┐ │
│  │  TERMINAL                                                  │ │
│  │  - init_screen() ──▶ stdscr                                │ │
│  │  - end_screen()                                            │ │
│  │  - setup_window()                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  DESENHO                                                   │ │
│  │  - safe_addstr()        - safe_addch()                     │ │
│  │  - draw_border()        - draw_hud()                       │ │
│  │  - draw_snake_and_food()                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LÓGICA                                                    │ │
│  │  - initial_state()                                         │ │
│  │  - next_direction()                                        │ │
│  │  - move_snake()        - grow_snake()                      │ │
│  │  - hit_wall_or_self()  - adjust_speed()                    │ │
│  │  - game_step()                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  RENDERIZAÇÃO                                              │ │
│  │  - render()                                                │ │
│  │  - game_over_screen()                                      │ │
│  │  - wait_restart_or_quit()                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  CONTROLE                                                  │ │
│  │  - game_loop()  ◀──────────────────────────────────────────┤ │
│  │  - main()                                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```


## 13. Glossário

| Termo | Definição |
|-------|-----------|
| **curses** | Biblioteca para manipular terminais de texto |
| **nodelay** | Modo não bloqueante para `getch()` |
| **frame** | Uma iteração do game loop |
| **FPS** | Frames por segundo (inversamente proporcional a `speed_ms`) |
| **HUD** | Heads-Up Display - informações mostradas na tela |
| **game loop** | Loop principal que atualiza e renderiza o jogo |
| **state** | Estado do jogo (snake, direction, food, score, etc) |

*Documento gerado em 2026. Versão do código: snake_text.py (345 linhas)*
