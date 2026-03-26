"""
Snake Game - Implementação Tkinter com Orientação a Objetos e Princípios SOLID
===============================================================================
- Arquitetura modular com classes bem definidas
- Interface gráfica com Tkinter (canvas)
- Controles apenas por teclado (Setas, WASD, P, Q, R)
- Compatível com Windows, Linux e macOS
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict, Callable
import tkinter as tk
from tkinter import font as tkfont
import random
import time


# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
@dataclass(frozen=True)
class GameConfig:
    """Configurações imutáveis do jogo."""
    # Velocidade
    INITIAL_SPEED_MS: int = 120
    MIN_SPEED_MS: int = 50
    SPEED_STEP_MS: int = 3
    
    # Dimensões do tabuleiro (em células)
    BOARD_WIDTH_CELLS: int = 40
    BOARD_HEIGHT_CELLS: int = 30
    CELL_SIZE: int = 15  # pixels por célula
    
    # Cores (RGB hex)
    COLOR_BACKGROUND: str = "#1a1a2e"
    COLOR_SNAKE_HEAD: str = "#00ff88"
    COLOR_SNAKE_BODY: str = "#00cc66"
    COLOR_FOOD: str = "#ff4444"
    COLOR_BORDER: str = "#444466"
    COLOR_TEXT: str = "#ffffff"
    COLOR_TEXT_DIM: str = "#888888"
    
    # Caracteres
    FOOD_CHAR: str = "*"
    SNAKE_HEAD_CHAR: str = "@"
    SNAKE_BODY_CHAR: str = "o"


# =============================================================================
# ENUMERAÇÕES
# =============================================================================
class Direction(Enum):
    """Direções como enumeração type-safe."""
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


class GameState(Enum):
    """Estados possíveis do jogo."""
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    QUIT = auto()


# =============================================================================
# VALUE OBJECTS
# =============================================================================
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


# =============================================================================
# ENTIDADES DE DOMÍNIO
# =============================================================================
class Snake:
    """Entidade Snake - Gerencia estado e comportamento da cobra."""
    
    def __init__(self, start_position: Position, initial_length: int = 3,
                 initial_direction: Direction = Direction.RIGHT):
        self._segments: List[Position] = self._create_initial_segments(
            start_position, initial_length, initial_direction
        )
        self._direction: Direction = initial_direction
        self._next_direction: Direction = initial_direction
        self._growing: bool = False
    
    @staticmethod
    def _create_initial_segments(start: Position, length: int, 
                                  direction: Direction) -> List[Position]:
        segments = [start]
        for i in range(1, length):
            seg_y = start.y - (direction.dy * i)
            seg_x = start.x - (direction.dx * i)
            segments.append(Position(seg_y, seg_x))
        return segments
    
    @property
    def head(self) -> Position:
        return self._segments[0]
    
    @property
    def direction(self) -> Direction:
        return self._direction
    
    @property
    def segments(self) -> List[Position]:
        return self._segments.copy()
    
    @property
    def length(self) -> int:
        return len(self._segments)
    
    def set_direction(self, new_direction: Direction) -> bool:
        if not self._direction.is_opposite(new_direction):
            self._next_direction = new_direction
            return True
        return False
    
    def move(self) -> Position:
        self._direction = self._next_direction
        new_head = self.head + self._direction
        self._segments.insert(0, new_head)
        
        if not self._growing:
            self._segments.pop()
        else:
            self._growing = False
        
        return new_head
    
    def grow(self):
        self._growing = True
    
    def check_self_collision(self) -> bool:
        return self.head in self._segments[1:]
    
    def occupies_position(self, position: Position) -> bool:
        return position in self._segments


class Food:
    """Entidade Food - Gerencia posição e respawn da comida."""
    
    def __init__(self, char: str = "*"):
        self._position: Optional[Position] = None
        self._char: str = char
    
    @property
    def position(self) -> Optional[Position]:
        return self._position
    
    @property
    def char(self) -> str:
        return self._char
    
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
    
    def is_at_position(self, position: Position) -> bool:
        return self._position == position if self._position else False


# =============================================================================
# SERVIÇOS DE DOMÍNIO
# =============================================================================
class CollisionService:
    """Serviço de colisão - Lógica de detecção de colisões."""
    
    def __init__(self, board_height: int, board_width: int):
        self._height = board_height
        self._width = board_width
    
    def check_wall_collision(self, position: Position) -> bool:
        return (
            position.y < 0 or
            position.y >= self._height or
            position.x < 0 or
            position.x >= self._width
        )
    
    def check_self_collision(self, snake: Snake) -> bool:
        return snake.check_self_collision()
    
    def check_any_collision(self, snake: Snake) -> bool:
        return (
            self.check_wall_collision(snake.head) or
            self.check_self_collision(snake)
        )


class SpeedService:
    """Serviço de velocidade - Calcula velocidade baseada no score."""
    
    def __init__(self, config: GameConfig):
        self._config = config
    
    def calculate_speed(self, score: int) -> int:
        target = self._config.INITIAL_SPEED_MS - (score * self._config.SPEED_STEP_MS)
        return max(self._config.MIN_SPEED_MS, 
                   min(self._config.INITIAL_SPEED_MS, target))


# =============================================================================
# INPUT HANDLER
# =============================================================================
class InputHandler:
    """Handler de entrada - Abstrai captura de teclado Tkinter."""
    
    def __init__(self, canvas: tk.Canvas):
        self._canvas = canvas
        self._keymap: Dict[str, Direction] = self._create_keymap()
        self._quit_callback: Optional[Callable] = None
        self._pause_callback: Optional[Callable] = None
        self._restart_callback: Optional[Callable] = None
        self._direction_callback: Optional[Callable[[Direction], None]] = None
    
    @staticmethod
    def _create_keymap() -> Dict[str, Direction]:
        return {
            'Up': Direction.UP,
            'Down': Direction.DOWN,
            'Left': Direction.LEFT,
            'Right': Direction.RIGHT,
            'w': Direction.UP,
            'W': Direction.UP,
            's': Direction.DOWN,
            'S': Direction.DOWN,
            'a': Direction.LEFT,
            'A': Direction.LEFT,
            'd': Direction.RIGHT,
            'D': Direction.RIGHT,
        }
    
    def bind_callbacks(self, 
                       on_quit: Callable = None,
                       on_pause: Callable = None,
                       on_restart: Callable = None,
                       on_direction: Callable[[Direction], None] = None):
        """Registra callbacks para eventos de teclado."""
        self._quit_callback = on_quit
        self._pause_callback = on_pause
        self._restart_callback = on_restart
        self._direction_callback = on_direction
        
        # Bind de teclas
        self._canvas.bind_all('<Key>', self._on_key_press)
        self._canvas.bind_all('<Escape>', lambda e: self._quit_callback())
    
    def _on_key_press(self, event):
        """Processa evento de tecla pressionada."""
        key = event.keysym
        
        # Q ou Escape = Sair
        if key in ('q', 'Q'):
            if self._quit_callback:
                self._quit_callback()
            return
        
        # P = Pausar
        if key in ('p', 'P'):
            if self._pause_callback:
                self._pause_callback()
            return
        
        # R = Reiniciar (apenas em GAME_OVER)
        if key in ('r', 'R'):
            if self._restart_callback:
                self._restart_callback()
            return
        
        # Setas/WASD = Mudar direção
        direction = self._keymap.get(key)
        if direction and self._direction_callback:
            self._direction_callback(direction)
    
    def get_direction(self, key: str) -> Optional[Direction]:
        """Converte tecla em direção, se válida."""
        return self._keymap.get(key)


# =============================================================================
# RENDERER
# =============================================================================
class Renderer(ABC):
    """Interface abstrata para renderizadores."""
    
    @abstractmethod
    def render(self, game_state: object) -> None:
        pass
    
    @abstractmethod
    def render_message(self, title: str, subtitle: str = "", 
                       instructions: str = "") -> None:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class TkinterRenderer(Renderer):
    """Renderizador específico para Tkinter Canvas."""
    
    def __init__(self, canvas: tk.Canvas, config: GameConfig, 
                 hud_label: tk.Label, score_label: tk.Label):
        self._canvas = canvas
        self._config = config
        self._hud_label = hud_label
        self._score_label = score_label
        
        # Configura fontes
        self._font_title = tkfont.Font(family="Consolas", size=24, weight="bold")
        self._font_subtitle = tkfont.Font(family="Consolas", size=16)
        self._font_instructions = tkfont.Font(family="Consolas", size=12)
        self._font_hud = tkfont.Font(family="Consolas", size=11)
        
        # Dimensões
        self._board_width_px = config.BOARD_WIDTH_CELLS * config.CELL_SIZE
        self._board_height_px = config.BOARD_HEIGHT_CELLS * config.CELL_SIZE
        
        # Configura canvas
        self._canvas.config(
            width=self._board_width_px,
            height=self._board_height_px,
            bg=config.COLOR_BACKGROUND,
            highlightthickness=0
        )
    
    def clear(self) -> None:
        """Limpa o canvas."""
        self._canvas.delete("all")
    
    def render(self, game: 'SnakeGame') -> None:
        """Renderiza o estado completo do jogo."""
        self.clear()
        self._draw_border()
        self._draw_snake(game.snake)
        self._draw_food(game.food)
        self._update_hud(game)
    
    def _draw_border(self):
        """Desenha borda do tabuleiro."""
        # Borda externa
        self._canvas.create_rectangle(
            0, 0,
            self._board_width_px, self._board_height_px,
            outline=self._config.COLOR_BORDER,
            width=2
        )
        
        # Grid sutil (opcional)
        for x in range(0, self._board_width_px, self._config.CELL_SIZE):
            self._canvas.create_line(
                x, 0, x, self._board_height_px,
                fill="#2a2a3e", width=1
            )
        for y in range(0, self._board_height_px, self._config.CELL_SIZE):
            self._canvas.create_line(
                0, y, self._board_width_px, y,
                fill="#2a2a3e", width=1
            )
    
    def _draw_snake(self, snake: Snake):
        """Desenha a cobra."""
        for i, segment in enumerate(snake.segments):
            x1 = segment.x * self._config.CELL_SIZE
            y1 = segment.y * self._config.CELL_SIZE
            x2 = x1 + self._config.CELL_SIZE
            y2 = y1 + self._config.CELL_SIZE
            
            # Cabeça vs Corpo
            color = (self._config.COLOR_SNAKE_HEAD if i == 0 
                     else self._config.COLOR_SNAKE_BODY)
            
            # Desenha retângulo arredondado
            padding = 2
            self._canvas.create_rectangle(
                x1 + padding, y1 + padding,
                x2 - padding, y2 - padding,
                fill=color,
                outline="",
                tags="snake"
            )
            
            # Olhos na cabeça
            if i == 0:
                self._draw_eyes(x1, y1, x2, y2, snake.direction)
    
    def _draw_eyes(self, x1: int, y1: int, x2: int, y2: int, 
                   direction: Direction):
        """Desenha olhos na cabeça da cobra."""
        eye_size = 3
        eye_color = "#ffffff"
        
        # Posição dos olhos baseada na direção
        if direction == Direction.UP:
            eye1 = (x1 + 4, y1 + 4)
            eye2 = (x2 - 7, y1 + 4)
        elif direction == Direction.DOWN:
            eye1 = (x1 + 4, y2 - 7)
            eye2 = (x2 - 7, y2 - 7)
        elif direction == Direction.LEFT:
            eye1 = (x1 + 4, y1 + 4)
            eye2 = (x1 + 4, y2 - 7)
        else:  # RIGHT
            eye1 = (x2 - 7, y1 + 4)
            eye2 = (x2 - 7, y2 - 7)
        
        self._canvas.create_oval(
            eye1[0], eye1[1], eye1[0] + eye_size, eye1[1] + eye_size,
            fill=eye_color, outline=""
        )
        self._canvas.create_oval(
            eye2[0], eye2[1], eye2[0] + eye_size, eye2[1] + eye_size,
            fill=eye_color, outline=""
        )
    
    def _draw_food(self, food: Food):
        """Desenha a comida."""
        if food.position:
            x1 = food.position.x * self._config.CELL_SIZE
            y1 = food.position.y * self._config.CELL_SIZE
            x2 = x1 + self._config.CELL_SIZE
            y2 = y1 + self._config.CELL_SIZE
            
            # Desenha como círculo
            padding = 3
            self._canvas.create_oval(
                x1 + padding, y1 + padding,
                x2 - padding, y2 - padding,
                fill=self._config.COLOR_FOOD,
                outline="#ff6666",
                width=2,
                tags="food"
            )
    
    def _update_hud(self, game: 'SnakeGame'):
        """Atualiza HUD com score e status."""
        fps = max(1, 1000 // max(1, game.current_speed_ms))
        
        # Score
        self._score_label.config(
            text=f"Score: {game.score}",
            fg=self._config.COLOR_TEXT,
            font=self._font_hud
        )
        
        # HUD info
        status = "PAUSADO" if game.state == GameState.PAUSED else "JOGANDO"
        status_color = "#ffaa00" if game.state == GameState.PAUSED else "#00ff88"
        
        hud_text = (
            f"Velocidade: {fps}fps  |  "
            f"Comprimento: {game.snake.length if game.snake else 0}  |  "
            f"Status: {status}"
        )
        
        self._hud_label.config(
            text=hud_text,
            fg=status_color,
            font=self._font_hud
        )
    
    def render_message(self, title: str, subtitle: str = "", 
                       instructions: str = "") -> None:
        """Renderiza mensagem centralizada (start screen, game over)."""
        self.clear()
        
        cx = self._board_width_px // 2
        cy = self._board_height_px // 2
        
        # Título
        self._canvas.create_text(
            cx, cy - 40,
            text=title,
            fill=self._config.COLOR_TEXT,
            font=self._font_title,
            tags="message"
        )
        
        # Subtítulo
        if subtitle:
            self._canvas.create_text(
                cx, cy,
                text=subtitle,
                fill=self._config.COLOR_TEXT,
                font=self._font_subtitle,
                tags="message"
            )
        
        # Instruções
        if instructions:
            self._canvas.create_text(
                cx, cy + 50,
                text=instructions,
                fill=self._config.COLOR_TEXT_DIM,
                font=self._font_instructions,
                tags="message"
            )
        
        # Borda decorativa
        self._canvas.create_rectangle(
            cx - 200, cy - 80, cx + 200, cy + 100,
            outline=self._config.COLOR_BORDER,
            width=2,
            tags="message"
        )
    
    def render_start_screen(self):
        """Renderiza tela inicial."""
        self.render_message(
            title="🐍 SNAKE GAME",
            subtitle="Jogo da Cobrinha",
            instructions=(
                "Controles: Setas ou WASD para mover\n"
                "P = Pausar  |  Q = Sair  |  R = Reiniciar\n\n"
                "Pressione qualquer tecla para começar..."
            )
        )
    
    def render_game_over(self, score: int, high_score: int = 0):
        """Renderiza tela de Game Over."""
        subtitle = f"Pontuação Final: {score}"
        if high_score > 0:
            subtitle += f"  |  Recorde: {high_score}"
        
        self.render_message(
            title="💀 GAME OVER",
            subtitle=subtitle,
            instructions=(
                "Pressione R para Reiniciar\n"
                "ou Q para Sair"
            )
        )


# =============================================================================
# SNAKE GAME FACADE
# =============================================================================
class SnakeGame:
    """Facade principal do jogo - Orquestra todos os componentes."""
    
    def __init__(self, root: tk.Tk, config: GameConfig = None):
        self._root = root
        self._config = config or GameConfig()
        
        # Componentes
        self._collision_service: Optional[CollisionService] = None
        self._speed_service: Optional[SpeedService] = None
        self._input_handler: Optional[InputHandler] = None
        self._renderer: Optional[TkinterRenderer] = None
        
        # Entidades
        self._snake: Optional[Snake] = None
        self._food: Optional[Food] = None
        
        # Estado
        self._state: GameState = GameState.RUNNING
        self._score: int = 0
        self._high_score: int = 0
        self._current_speed_ms: int = self._config.INITIAL_SPEED_MS
        
        # Timing
        self._last_update_time: float = 0
        self._game_loop_id: Optional[int] = None
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do usuário."""
        self._root.title("Snake Game - Tkinter")
        self._root.resizable(False, False)
        self._root.configure(bg=self._config.COLOR_BACKGROUND)
        
        # Frame principal
        main_frame = tk.Frame(self._root, bg=self._config.COLOR_BACKGROUND)
        main_frame.pack(padx=10, pady=10)
        
        # Frame do HUD (topo)
        hud_frame = tk.Frame(main_frame, bg=self._config.COLOR_BACKGROUND)
        hud_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Score label
        self._score_label = tk.Label(
            hud_frame, 
            text="Score: 0",
            bg=self._config.COLOR_BACKGROUND,
            fg=self._config.COLOR_TEXT
        )
        self._score_label.pack(side=tk.LEFT, padx=10)
        
        # HUD info label
        self._hud_label = tk.Label(
            hud_frame,
            text="",
            bg=self._config.COLOR_BACKGROUND,
            fg=self._config.COLOR_TEXT
        )
        self._hud_label.pack(side=tk.RIGHT, padx=10)
        
        # Canvas do jogo
        self._canvas = tk.Canvas(
            main_frame,
            width=self._config.BOARD_WIDTH_CELLS * self._config.CELL_SIZE,
            height=self._config.BOARD_HEIGHT_CELLS * self._config.CELL_SIZE,
            bg=self._config.COLOR_BACKGROUND,
            highlightthickness=0
        )
        self._canvas.pack()
        
        # Frame de instruções (rodapé)
        info_frame = tk.Frame(main_frame, bg=self._config.COLOR_BACKGROUND)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        instructions = (
            "⬆⬇⬅➡ ou WASD: Mover  |  P: Pausar  |  Q: Sair  |  R: Reiniciar"
        )
        info_label = tk.Label(
            info_frame,
            text=instructions,
            bg=self._config.COLOR_BACKGROUND,
            fg=self._config.COLOR_TEXT_DIM,
            font=tkfont.Font(family="Consolas", size=9)
        )
        info_label.pack()
        
        # Centraliza janela na tela
        self._center_window()
    
    def _center_window(self):
        """Centraliza a janela na tela."""
        self._root.update_idletasks()
        
        width = self._root.winfo_width()
        height = self._root.winfo_height()
        x = (self._root.winfo_screenwidth() // 2) - (width // 2)
        y = (self._root.winfo_screenheight() // 2) - (height // 2)
        
        self._root.geometry(f'{width}x{height}+{x}+{y}')
    
    @property
    def snake(self) -> Snake:
        return self._snake
    
    @property
    def food(self) -> Food:
        return self._food
    
    @property
    def state(self) -> GameState:
        return self._state
    
    @property
    def score(self) -> int:
        return self._score
    
    @property
    def current_speed_ms(self) -> int:
        return self._current_speed_ms
    
    def initialize(self) -> bool:
        """Inicializa todos os componentes do jogo."""
        # Inicializa renderer
        self._renderer = TkinterRenderer(
            self._canvas, 
            self._config,
            self._hud_label,
            self._score_label
        )
        
        # Inicializa serviços
        self._collision_service = CollisionService(
            self._config.BOARD_HEIGHT_CELLS,
            self._config.BOARD_WIDTH_CELLS
        )
        self._speed_service = SpeedService(self._config)
        
        # Inicializa input handler
        self._input_handler = InputHandler(self._canvas)
        self._input_handler.bind_callbacks(
            on_quit=self._on_quit,
            on_pause=self._on_pause,
            on_restart=self._on_restart,
            on_direction=self._on_direction
        )
        
        # Inicializa estado do jogo
        self._reset_game_state()
        
        return True
    
    def _reset_game_state(self):
        """Reseta estado do jogo para valores iniciais."""
        center_y = self._config.BOARD_HEIGHT_CELLS // 2
        center_x = self._config.BOARD_WIDTH_CELLS // 2
        start_position = Position(center_y, center_x)
        
        self._snake = Snake(start_position)
        self._food = Food(self._config.FOOD_CHAR)
        self._state = GameState.RUNNING
        self._score = 0
        self._current_speed_ms = self._config.INITIAL_SPEED_MS
        
        # Posiciona comida inicial
        available = self._get_available_positions()
        self._food.respawn(available, self._snake.segments)
    
    def _get_available_positions(self) -> List[Position]:
        """Retorna todas as posições jogáveis disponíveis."""
        positions = []
        for y in range(self._config.BOARD_HEIGHT_CELLS):
            for x in range(self._config.BOARD_WIDTH_CELLS):
                positions.append(Position(y, x))
        return positions
    
    def run(self):
        """Executa o jogo (inicia game loop)."""
        self.initialize()
        self._show_start_screen = True
        self._game_started = False
        
        # Renderiza tela inicial
        self._renderer.render_start_screen()
        
        # Inicia game loop
        self._last_update_time = time.time()
        self._game_loop()
        
        # Inicia mainloop do Tkinter
        self._root.mainloop()
    
    def _game_loop(self):
        """Game loop principal (chamado recursivamente via after)."""
        if self._state == GameState.QUIT:
            self._root.quit()
            return
        
        current_time = time.time()
        elapsed_ms = (current_time - self._last_update_time) * 1000
        
        # Atualiza apenas se passou tempo suficiente
        if elapsed_ms >= self._current_speed_ms:
            self._last_update_time = current_time
            
            if self._show_start_screen:
                self._show_start_screen = False
                self._game_started = True
            elif self._state == GameState.RUNNING:
                self._update_game_logic()
        
        # Renderiza sempre
        if self._game_started and self._state != GameState.GAME_OVER:
            self._renderer.render(self)
        
        # Agenda próxima chamada
        self._game_loop_id = self._root.after(16, self._game_loop)  # ~60 FPS
    
    def _on_direction(self, direction: Direction):
        """Callback para mudança de direção."""
        if self._state == GameState.RUNNING and self._snake:
            self._snake.set_direction(direction)
            # Inicia jogo na primeira tecla de direção
            if self._show_start_screen:
                self._show_start_screen = False
                self._game_started = True
    
    def _on_pause(self):
        """Callback para pausar/retomar."""
        if self._state == GameState.RUNNING:
            self._state = GameState.PAUSED
            self._renderer.render_message(
                title="⏸ PAUSADO",
                subtitle=f"Score: {self._score}",
                instructions="Pressione P para continuar"
            )
        elif self._state == GameState.PAUSED:
            self._state = GameState.RUNNING
            self._last_update_time = time.time()
    
    def _on_restart(self):
        """Callback para reiniciar jogo."""
        if self._state == GameState.GAME_OVER:
            self._reset_game_state()
            self._state = GameState.RUNNING
            self._last_update_time = time.time()
            self._game_started = True
    
    def _on_quit(self):
        """Callback para sair do jogo."""
        self._state = GameState.QUIT
        if self._game_loop_id:
            self._root.after_cancel(self._game_loop_id)
        self._root.quit()
        self._root.destroy()
    
    def _update_game_logic(self):
        """Atualiza lógica do jogo (movimento, colisão, comida)."""
        if not self._snake or not self._food:
            return
        
        # Move cobra
        self._snake.move()
        
        # Verifica colisões
        if self._collision_service.check_any_collision(self._snake):
            self._state = GameState.GAME_OVER
            if self._score > self._high_score:
                self._high_score = self._score
            self._renderer.render_game_over(self._score, self._high_score)
            return
        
        # Verifica se comeu
        if self._food.is_at_position(self._snake.head):
            self._snake.grow()
            self._score += 1
            self._current_speed_ms = self._speed_service.calculate_speed(self._score)
            
            # Respawn comida
            available = self._get_available_positions()
            self._food.respawn(available, self._snake.segments)


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    """Ponto de entrada principal."""
    root = tk.Tk()
    
    # Configurações adicionais
    root.configure(bg="#1a1a2e")
    
    # Cria e executa jogo
    game = SnakeGame(root)
    game.run()


if __name__ == "__main__":
    main()