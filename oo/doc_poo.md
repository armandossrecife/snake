# 🐍 Explicação Passo a Passo: Snake Game em Python com Orientação a Objetos

Detalhadamente cada parte do código, destacando os conceitos de POO e princípios SOLID aplicados.

---

## 📋 **Visão Geral da Arquitetura**

```
┌─────────────────────────────────────────────────────────────────┐
│                         ARQUITETURA DO SISTEMA                  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   SNAKE     │  │    FOOD     │  │    POSITION (Value)     │ │
│  │  (Entity)   │  │  (Entity)   │  │       (Value Object)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Collision  │  │    Speed    │  │     INPUT HANDLER       │ │
│  │   Service   │  │   Service   │  │    (Infrastructure)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  RENDERER   │  │  SnakeGame  │  │   TERMINAL MANAGER      │ │
│  │ (Interface) │  │  (Facade)   │  │    (Resource Mgmt)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **1. Imports e Configurações Iniciais**

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict
import curses
import random
import time
```

| **Import** | **Propósito** |
|-----------|--------------|
| `annotations` | Permite usar tipos ainda não definidos (forward references) |
| `ABC, abstractmethod` | Cria classes abstratas (interface) |
| `dataclass` | Reduz boilerplate para classes de dados |
| `Enum, auto` | Cria enumerações type-safe |
| `typing` | Type hints para melhor legibilidade e IDE support |
| `curses` | Biblioteca para controle de terminal |
| `random` | Geração de posições aleatórias |
| `time` | Controle de framerate |

---

## ⚙️ **2. GameConfig - Configurações Imutáveis**

```python
@dataclass(frozen=True)
class GameConfig:
    """Configurações imutáveis do jogo."""
    INITIAL_SPEED_MS: int = 120
    MIN_SPEED_MS: int = 50
    SPEED_STEP_MS: int = 3
    BORDER_PADDING: int = 1
    MIN_HEIGHT: int = 20
    MIN_WIDTH: int = 40
    
    FOOD_CHAR: str = "*"
    SNAKE_HEAD_CHAR: str = "@"
    SNAKE_BODY_CHAR: str = "o"
    WALL_CHAR: str = "#"
```

### 🔍 Conceitos Aplicados:

| **Conceito** | **Explicação** |
|-------------|---------------|
| `@dataclass` | Gera automaticamente `__init__`, `__repr__`, `__eq__` |
| `frozen=True` | Torna a instância **imutável** (não pode modificar após criação) |
| **Single Source of Truth** | Todas as configurações em um único lugar |

### ✅ Vantagens:
- **Imutabilidade**: Previne mudanças acidentais em runtime
- **Centralização**: Fácil manutenção (muda em um lugar, afeta todo o jogo)
- **Type Safety**: Type hints permitem verificação estática

---

## 🧭 **3. Enumerações (Direction e GameState)**

### **Direction Enum**
```python
class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    
    @property
    def dy(self) -> int:
        return self.value[0]
    
    @property
    def dx(self) -> int:
        return self.value[1]
    
    def is_opposite(self, other: 'Direction') -> bool:
        return self.dy == -other.dy and self.dx == -other.dx
```

### 📊 Por que Enum em vez de constantes?

| **Abordagem** | **Vantagens** | **Desvantagens** |
|--------------|--------------|-----------------|
| **Constantes** (`UP = (-1, 0)`) | Simples | Sem type safety, erros silenciosos |
| **Enum** | Type-safe, IDE autocomplete, validação | Um pouco mais verboso |

### 🔑 Métodos Importantes:

```python
# Exemplo de uso:
direction = Direction.UP
print(direction.dy)  # -1
print(direction.dx)  # 0

# Verifica se direções são opostas (evita cobra voltar 180°)
Direction.UP.is_opposite(Direction.DOWN)  # True
Direction.UP.is_opposite(Direction.LEFT)  # False
```

### **GameState Enum**
```python
class GameState(Enum):
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    QUIT = auto()
```

Gerencia o **estado da máquina de estados** do jogo.

---

## 📍 **4. Position - Value Object**

```python
@dataclass(frozen=True)
class Position:
    """Posição (x, y) no tabuleiro - Value Object imutável."""
    y: int
    x: int
    
    def __add__(self, direction: Direction) -> 'Position':
        return Position(self.y + direction.dy, self.x + direction.dx)
    
    def __iter__(self):
        yield self.y
        yield self.x
```

### 🎯 Conceito: **Value Object** (Domain-Driven Design)

| **Característica** | **Descrição** |
|-------------------|--------------|
| **Imutável** | Uma vez criado, não muda |
| **Sem identidade** | Igualdade baseada nos valores (y, x) |
| **Substituível** | Pode trocar sem efeitos colaterais |

### ✨ Métodos Especiais:

```python
# __add__: Permite soma com Direction
pos = Position(10, 10)
new_pos = pos + Direction.RIGHT  # Position(10, 11)

# __iter__: Permite unpacking
y, x = position  # Funciona como tupla!
```

---

## 🐍 **5. Snake - Entidade de Domínio**

```python
class Snake:
    """Entidade Snake - Gerencia estado e comportamento da cobra."""
    
    def __init__(self, start_position: Position, initial_length: int = 3,
                 initial_direction: Direction = Direction.RIGHT):
        self._segments: List[Position] = self._create_initial_segments(...)
        self._direction: Direction = initial_direction
        self._next_direction: Direction = initial_direction
        self._growing: bool = False
```

### 🔒 Encapsulamento:

| **Atributo** | **Visibilidade** | **Motivo** |
|-------------|-----------------|-----------|
| `_segments` | Private (`_`) | Não modificar diretamente |
| `_direction` | Private | Controlado via `set_direction()` |
| `_next_direction` | Private | Buffer para evitar múltiplas mudanças no mesmo frame |
| `_growing` | Private | Estado interno de crescimento |

### 📐 Métodos Públicos (API da Classe):

```python
# Properties (leitura apenas)
@property
def head(self) -> Position: ...

@property
def segments(self) -> List[Position]:
    return self._segments.copy()  # ← Retorna CÓPIA (protege estado interno)

# Métodos de comportamento
def set_direction(new_direction: Direction) -> bool: ...
def move() -> Position: ...
def grow(): ...
def check_self_collision() -> bool: ...
```

### 🔄 Como o Movimento Funciona:

```python
def move(self) -> Position:
    # 1. Atualiza direção atual com a próxima (buffer)
    self._direction = self._next_direction
    
    # 2. Calcula nova cabeça
    new_head = self.head + self._direction
    
    # 3. Adiciona nova cabeça na lista
    self._segments.insert(0, new_head)
    
    # 4. Remove cauda (se não estiver crescendo)
    if not self._growing:
        self._segments.pop()
    else:
        self._growing = False  # Reseta flag após crescer
    
    return new_head
```

### 📊 Diagrama do Movimento:

```
Antes:  [Cabeça]→[Corpo1]→[Corpo2]
                ↓
Depois: [NovaCabeça]→[Cabeça]→[Corpo1]  (Corpo2 removido)
```

---

## 🍎 **6. Food - Entidade de Domínio**

```python
class Food:
    """Entidade Food - Gerencia posição e respawn da comida."""
    
    def __init__(self, char: str = "*"):
        self._position: Optional[Position] = None
        self._char: str = char
    
    def respawn(self, available_positions: List[Position], 
                occupied_positions: List[Position]) -> bool:
        free_positions = [
            pos for pos in available_positions 
            if pos not in occupied_positions
        ]
        
        if not free_positions:
            self._position = None
            return False
        
        self._position = random.choice(free_positions)
        return True
```

### 🎯 Responsabilidades:

1. **Manter posição atual** da comida
2. **Gerar nova posição** aleatória livre
3. **Verificar colisão** com a cabeça da cobra

### 🔍 Por que `Optional[Position]`?

```python
# A comida pode NÃO ter posição (ex: sem espaços livres)
self._position: Optional[Position] = None

# Isso força o desenvolvedor a verificar antes de usar:
if food.position:  # ← IDE avisa se não verificar
    y, x = food.position
```

---

## 🛠️ **7. Serviços de Domínio**

### **CollisionService**
```python
class CollisionService:
    """Serviço de colisão - Lógica de detecção de colisões."""
    
    def __init__(self, board_height: int, board_width: int, 
                 border_padding: int = 1):
        self._height = board_height
        self._width = board_width
        self._padding = border_padding
    
    def check_wall_collision(self, position: Position) -> bool: ...
    def check_self_collision(self, snake: Snake) -> bool: ...
    def check_any_collision(self, snake: Snake) -> bool: ...
```

### 🎯 **SRP (Single Responsibility Principle)**:
- **Única responsabilidade**: Detectar colisões
- **Não sabe** sobre Snake, Food, Game, Renderer
- **Fácil de testar** isoladamente

### **SpeedService**
```python
class SpeedService:
    """Serviço de velocidade - Calcula velocidade baseada no score."""
    
    def __init__(self, config: GameConfig):
        self._config = config
    
    def calculate_speed(self, score: int) -> int:
        target = self._config.INITIAL_SPEED_MS - (score * self._config.SPEED_STEP_MS)
        return max(self._config.MIN_SPEED_MS, 
                   min(self._config.INITIAL_SPEED_MS, target))
```

### 🎯 **DIP (Dependency Inversion Principle)**:
- Depende de `GameConfig` (abstração de configuração)
- Não depende de implementação concreta do jogo

---

## ⌨️ **8. InputHandler - Infraestrutura**

```python
class InputHandler:
    """Handler de entrada - Abstrai captura de teclado."""
    
    def __init__(self, stdscr):
        self._stdscr = stdscr
        self._keymap: Dict[int, Direction] = self._create_keymap()
    
    def get_key(self) -> int: ...
    def get_direction(self, key: int) -> Optional[Direction]: ...
    def is_quit_command(self, key: int) -> bool: ...
    def is_pause_command(self, key: int) -> bool: ...
    def is_restart_command(self, key: int) -> bool: ...
```

### 🎯 **Separação de Responsabilidades**:

| **Camada** | **Responsabilidade** |
|-----------|---------------------|
| `InputHandler` | Capturar e interpretar teclas |
| `SnakeGame` | Decidir o que fazer com a entrada |

### 🔑 Mapeamento de Teclas:

```python
{
    curses.KEY_UP: Direction.UP,
    ord('w'): Direction.UP,
    ord('W'): Direction.UP,
    ord('s'): Direction.DOWN,
    # ... etc
}
```

---

## 🎨 **9. Renderer - Interface e Implementação**

### **Interface Abstrata (ISP + DIP)**
```python
class Renderer(ABC):
    """Interface abstrata para renderizadores."""
    
    @abstractmethod
    def render(self, game_state: object) -> None:
        pass
    
    @abstractmethod
    def render_message(self, message: str, y: int = 1, x: int = 1) -> None:
        pass
```

### 🎯 **Por que Interface Abstrata?**

1. **ISP (Interface Segregation)**: Interface pequena, focada
2. **DIP (Dependency Inversion)**: `SnakeGame` depende da interface, não da implementação
3. **OCP (Open/Closed)**: Pode criar novos renderizadores sem modificar o jogo

```python
# Futura extensão possível:
class WebRenderer(Renderer): ...      # Renderiza em browser
class NetworkRenderer(Renderer): ...  # Envia para cliente remoto
```

### **CursesRenderer (Implementação Concreta)**
```python
class CursesRenderer(Renderer):
    COLOR_SNAKE = 1
    COLOR_FOOD = 2
    COLOR_HUD = 3
    COLOR_BORDER = 4
    
    def __init__(self, stdscr, config: GameConfig):
        self._stdscr = stdscr
        self._config = config
        self._setup_colors()
```

### 🎨 Sistema de Cores:

```python
curses.init_pair(self.COLOR_SNAKE, curses.COLOR_GREEN, -1)   # Cobra verde
curses.init_pair(self.COLOR_FOOD, curses.COLOR_RED, -1)      # Comida vermelha
curses.init_pair(self.COLOR_HUD, curses.COLOR_CYAN, -1)      # HUD ciano
curses.init_pair(self.COLOR_BORDER, curses.COLOR_WHITE, -1)  # Borda branca
```

### 🛡️ **Tratamento de Erros (Robustez)**:

```python
def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0):
    try:
        self._stdscr.addstr(y, x, text, attr)
    except (curses.error, OverflowError):
        try:
            # Fallback para ASCII (evita crash no macOS)
            safe_text = text.encode('ascii', 'ignore').decode('ascii') or '#'
            self._stdscr.addstr(y, x, safe_text, attr)
        except Exception:
            pass  # Falha silenciosa é melhor que crash
```

---

## 🎮 **10. SnakeGame - Facade Principal**

```python
class SnakeGame:
    """Facade principal do jogo - Orquestra todos os componentes."""
    
    def __init__(self, stdscr, config: GameConfig = None):
        self._stdscr = stdscr
        self._config = config or GameConfig()
        
        # Serviços (inicializados depois)
        self._collision_service: Optional[CollisionService] = None
        self._speed_service: Optional[SpeedService] = None
        self._input_handler: Optional[InputHandler] = None
        self._renderer: Optional[CursesRenderer] = None
        
        # Entidades (inicializadas depois)
        self._snake: Optional[Snake] = None
        self._food: Optional[Food] = None
        
        # Estado do jogo
        self._state: GameState = GameState.RUNNING
        self._score: int = 0
        self._current_speed_ms: int = self._config.INITIAL_SPEED_MS
```

### 🎯 **Padrão Facade**:

```
┌─────────────────────────────────────────┐
│           CLIENTE (main)                │
│                                         │
│         game = SnakeGame(stdscr)        │
│         game.run()                      │
│                                         │
│  ← Não precisa saber sobre:             │
│     - Snake, Food, Position             │
│     - CollisionService, SpeedService    │
│     - InputHandler, Renderer            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         SnakeGame (Facade)              │
│                                         │
│  ← Orquestra todos os componentes       │
│  ← Interface simples para o cliente     │
└─────────────────────────────────────────┘
```

### 🔄 **Método initialize() - Correção Importante**:

```python
def initialize(self) -> bool:
    height, width = self._stdscr.getmaxyx()
    
    # ✅ CORREÇÃO: Criar renderer ANTES de verificar tamanho
    self._renderer = CursesRenderer(self._stdscr, self._config)
    self._input_handler = InputHandler(self._stdscr)
    
    # Verifica tamanho mínimo
    if height < self._config.MIN_HEIGHT or width < self._config.MIN_WIDTH:
        return False  # ← Renderer já existe, pode mostrar aviso
    
    # Inicializa restante...
    self._collision_service = CollisionService(...)
    self._speed_service = SpeedService(...)
    self._reset_game_state(height, width)
    
    return True
```

### ⚠️ **Por que essa ordem importa?**

```python
# ❌ ERRADO:
if terminal_pequeno:
    return False
self._renderer = CursesRenderer(...)  # ← Nunca executa se terminal pequeno!

# Depois no run():
if not self.initialize():
    self._renderer.render_message(...)  # ← ERRO: _renderer é None!

# ✅ CORRETO:
self._renderer = CursesRenderer(...)  # ← Sempre cria primeiro
if terminal_pequeno:
    return False  # ← Agora _renderer existe!
```

### 🔄 **Game Loop Principal**:

```python
def run(self):
    if not self.initialize():
        # Mostra erro e sai
        self._renderer.render_message(...)
        return
    
    # Tela inicial
    self._renderer.render_start_screen()
    self._stdscr.getch()  # Aguarda tecla
    
    # LOOP PRINCIPAL
    while self._state != GameState.QUIT:
        start_time = time.time()
        
        # 1. RENDER
        self._renderer.render(self)
        
        # 2. INPUT
        self._process_input()
        
        # 3. UPDATE (apenas se RUNNING)
        if self._state == GameState.RUNNING:
            self._update_game_logic()
        
        # 4. TIMING
        self._control_frame_rate(start_time)
```

### 📊 **Fluxo do Game Loop**:

```
┌─────────────────────────────────────────────────────────┐
│                    GAME LOOP                            │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────┐│
│  │ RENDER  │ →  │  INPUT  │ →  │  UPDATE │ →  │SLEEP ││
│  │ (Draw)  │    │ (Key)   │    │ (Logic) │    │(FPS) ││
│  └─────────┘    └─────────┘    └─────────┘    └──────┘│
│       ↑                                               │
│       └───────────────────────────────────────────────│
│                      (Repete até QUIT)                │
└─────────────────────────────────────────────────────────┘
```

### 🎯 **Processamento de Input**:

```python
def _process_input(self):
    key = self._input_handler.get_key()
    
    # Q = Sair
    if self._input_handler.is_quit_command(key):
        self._state = GameState.QUIT
        return
    
    # P = Pausar/Retomar
    if self._input_handler.is_pause_command(key):
        if self._state == GameState.RUNNING:
            self._state = GameState.PAUSED
        elif self._state == GameState.PAUSED:
            self._state = GameState.RUNNING
        return
    
    # R = Reiniciar (apenas em GAME_OVER)
    if self._state == GameState.GAME_OVER:
        if self._input_handler.is_restart_command(key):
            self._restart_game()
        return
    
    # Setas/WASD = Mudar direção (apenas RUNNING)
    if self._state == GameState.RUNNING:
        direction = self._input_handler.get_direction(key)
        if direction:
            self._snake.set_direction(direction)
```

### 🎯 **Lógica de Update**:

```python
def _update_game_logic(self):
    # 1. Move cobra
    self._snake.move()
    
    # 2. Verifica colisões
    if self._collision_service.check_any_collision(self._snake):
        self._state = GameState.GAME_OVER
        self._renderer.render_game_over(self._score)
        self._handle_game_over()
        return
    
    # 3. Verifica se comeu
    if self._food.is_at_position(self._snake.head):
        self._snake.grow()
        self._score += 1
        self._current_speed_ms = self._speed_service.calculate_speed(self._score)
        
        # Respawn comida
        height, width = self._stdscr.getmaxyx()
        available = self._get_available_positions(height, width)
        self._food.respawn(available, self._snake.segments)
```

### ⏱️ **Controle de Framerate**:

```python
def _control_frame_rate(self, start_time: float):
    elapsed_ms = int((time.time() - start_time) * 1000)
    remaining = self._current_speed_ms - elapsed_ms
    
    if remaining > 0:
        time.sleep(remaining / 1000.0)
```

### 📊 Exemplo de Timing:

```
speed_ms = 120ms (8.3 FPS)
elapsed_ms = 45ms (tempo para render + update)
remaining = 75ms
time.sleep(0.075)  # ← Espera para completar 120ms
```

---

## 🖥️ **11. TerminalManager - Gerenciamento de Recursos**

```python
class TerminalManager:
    """Gerencia recursos do terminal (RAII pattern)."""
    
    def __init__(self):
        self._stdscr = None
    
    def __enter__(self):
        self._stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self._stdscr.keypad(True)
        return self._stdscr
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._stdscr:
            self._stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        curses.endwin()
```

### 🎯 **Padrão: Context Manager (RAII)**

| **Conceito** | **Descrição** |
|-------------|--------------|
| **RAII** | Resource Acquisition Is Initialization |
| **`__enter__`** | Adquire recurso (inicializa terminal) |
| **`__exit__`** | Libera recurso (restaura terminal) |
| **Garantia** | `__exit__` sempre executa, mesmo com exceções |

### ✅ Vantagens:

```python
# COM Context Manager (SEGURO):
with TerminalManager() as stdscr:
    game = SnakeGame(stdscr)
    game.run()
# ← Terminal SEMPRE restaurado, mesmo se crashar

# SEM Context Manager (ARRISCADO):
stdscr = init_screen()
game.run()  # ← Se crashar aqui, terminal fica bagunçado!
end_screen(stdscr)  # ← Nunca executa!
```

---

## 🚀 **12. Entry Point (main)**

```python
def main():
    """Ponto de entrada principal."""
    with TerminalManager() as stdscr:
        game = SnakeGame(stdscr)
        game.run()


if __name__ == "__main__":
    curses.wrapper(lambda stdscr: main())
```

### 🔍 **Por que `curses.wrapper()`?**

```python
# curses.wrapper faz:
try:
    stdscr = curses.initscr()
    # ... configurações ...
    return func(stdscr, *args, **kwds)
finally:
    curses.endwin()  # ← Sempre restaura terminal

# É uma segurança EXTRA além do TerminalManager
# (defesa em profundidade)
```

---

## 📊 **Resumo dos Princípios SOLID Aplicados**

| **Princípio** | **Onde** | **Como** |
|--------------|----------|----------|
| **S - SRP** | Todas as classes | Cada classe tem UMA responsabilidade |
| **O - OCP** | `Renderer` interface | Pode adicionar novos renderizadores sem modificar `SnakeGame` |
| **L - LSP** | `Direction` enum | Qualquer `Direction` pode substituir outra |
| **I - ISP** | `Renderer` interface | Interface pequena, não força métodos não usados |
| **D - DIP** | `SnakeGame` | Depende de abstrações (`Renderer`, `CollisionService`) |

---

## 🗂️ **Diagrama de Classes Completo**

```
┌─────────────────────────────────────────────────────────────────┐
│                        GAME CONFIG                              │
│  @dataclass(frozen=True)                                        │
│  - INITIAL_SPEED_MS, MIN_SPEED_MS, SPEED_STEP_MS, etc.          │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (usa)
┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐
│  Direction  │  │  GameState  │  │         Position            │
│   (Enum)    │  │   (Enum)    │  │      @dataclass(frozen)     │
│  UP,DOWN... │  │RUNNING,etc. │  │      y, x, __add__, etc.    │
└─────────────┘  └─────────────┘  └─────────────────────────────┘
       ↓                ↓                    ↓
┌─────────────┐  ┌─────────────┐            ↓
│    Snake    │  │    Food     │            ↓
│  (Entity)   │  │  (Entity)   │            ↓
│  segments,  │  │  position,  │            ↓
│  direction, │  │  respawn()  │            ↓
│  move()     │  │  char       │            ↓
└─────────────┘  └─────────────┘            ↓
       ↓                ↓                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    COLLISION SERVICE                            │
│  check_wall_collision(), check_self_collision()                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SPEED SERVICE                              │
│  calculate_speed(score)                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      INPUT HANDLER                              │
│  get_key(), get_direction(), is_*_command()                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        RENDERER (ABC)                           │
│  render(), render_message()                                     │
│       ↑                                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  CURSES RENDERER                         │   │
│  │  _draw_border(), _draw_hud(), _draw_snake(), etc.        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       SNAKE GAME                                │
│                    (Facade Principal)                           │
│  initialize(), run(), _process_input(), _update_game_logic()    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     TERMINAL MANAGER                            │
│                  (Context Manager / RAII)                       │
│  __enter__(), __exit__()                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ **Conclusão**

Esta implementação demonstra:

1. **POO bem aplicada**: Classes coesas, encapsulamento, responsabilidades claras
2. **SOLID**: Todos os 5 princípios aplicados de forma prática
3. **Padrões de Projeto**: Facade, Strategy (Renderer), Context Manager (RAII)
4. **Robustez**: Tratamento de erros, compatibilidade macOS/Linux
5. **Manutenibilidade**: Fácil estender (novos renderizadores, serviços, etc.)

**Comparação com versão funcional:**

| **Aspecto** | **Funcional** | **OO (esta versão)** |
|------------|--------------|---------------------|
| Linhas | ~487 | ~650 |
| Classes | 0 | 10 |
| Testabilidade | Alta | Alta+ (mocks) |
| Extensibilidade | Média | Alta |
| Curva de aprendizado | Baixa | Média |
| Ideal para | Protótipos, scripts | Projetos em produção |

Ambas são válidas - a escolha depende do **contexto do projeto**! 🎮