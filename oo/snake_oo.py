"""
Snake Game - Implementação Orientada a Objetos com Princípios SOLID
===============================================================================
- Arquitetura modular com classes bem definidas
- Compatível com Linux e macOS (curses + ASCII)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict
import curses
import random
import time

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
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
    
    def __init__(self, board_height: int, board_width: int, 
                 border_padding: int = 1):
        self._height = board_height
        self._width = board_width
        self._padding = border_padding
    
    def check_wall_collision(self, position: Position) -> bool:
        return (
            position.y <= self._padding or
            position.y >= self._height - self._padding - 1 or
            position.x <= self._padding or
            position.x >= self._width - self._padding - 1
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
    """Handler de entrada - Abstrai captura de teclado."""
    
    def __init__(self, stdscr):
        self._stdscr = stdscr
        self._keymap: Dict[int, Direction] = self._create_keymap()
    
    @staticmethod
    def _create_keymap() -> Dict[int, Direction]:
        return {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
            ord('w'): Direction.UP,
            ord('W'): Direction.UP,
            ord('s'): Direction.DOWN,
            ord('S'): Direction.DOWN,
            ord('a'): Direction.LEFT,
            ord('A'): Direction.LEFT,
            ord('d'): Direction.RIGHT,
            ord('D'): Direction.RIGHT,
        }
    
    def get_key(self) -> int:
        return self._stdscr.getch()
    
    def get_direction(self, key: int) -> Optional[Direction]:
        return self._keymap.get(key)
    
    def is_quit_command(self, key: int) -> bool:
        return key in (ord('q'), ord('Q'))
    
    def is_pause_command(self, key: int) -> bool:
        return key in (ord('p'), ord('P'))
    
    def is_restart_command(self, key: int) -> bool:
        return key in (ord('r'), ord('R'))


# =============================================================================
# RENDERER
# =============================================================================
class Renderer(ABC):
    """Interface abstrata para renderizadores."""
    
    @abstractmethod
    def render(self, game_state: object) -> None:
        pass
    
    @abstractmethod
    def render_message(self, message: str, y: int = 1, x: int = 1) -> None:
        """Renderiza mensagem genérica (para erros/avisos)."""
        pass


class CursesRenderer(Renderer):
    """Renderizador específico para curses."""
    
    COLOR_SNAKE = 1
    COLOR_FOOD = 2
    COLOR_HUD = 3
    COLOR_BORDER = 4
    
    def __init__(self, stdscr, config: GameConfig):
        self._stdscr = stdscr
        self._config = config
        self._setup_colors()
    
    def _setup_colors(self):
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(self.COLOR_SNAKE, curses.COLOR_GREEN, -1)
            curses.init_pair(self.COLOR_FOOD, curses.COLOR_RED, -1)
            curses.init_pair(self.COLOR_HUD, curses.COLOR_CYAN, -1)
            curses.init_pair(self.COLOR_BORDER, curses.COLOR_WHITE, -1)
        except curses.error:
            pass
    
    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0):
        try:
            self._stdscr.addstr(y, x, text, attr)
        except (curses.error, OverflowError):
            try:
                safe_text = text.encode('ascii', 'ignore').decode('ascii') or '#'
                self._stdscr.addstr(y, x, safe_text, attr)
            except Exception:
                pass
    
    def _safe_addch(self, y: int, x: int, char: str, attr: int = 0):
        try:
            self._stdscr.addch(y, x, char, attr)
        except (curses.error, OverflowError, TypeError):
            self._safe_addstr(y, x, str(char)[:1] or '#', attr)
    
    def render(self, game: 'SnakeGame') -> None:
        self._stdscr.erase()
        self._draw_border()
        self._draw_hud(game)
        self._draw_snake(game.snake)
        self._draw_food(game.food)
        self._stdscr.refresh()
    
    def render_message(self, message: str, y: int = 1, x: int = 1, 
                       attr: int = 0) -> None:
        """Renderiza mensagem genérica - USADO PARA AVISOS DE ERRO."""
        self._safe_addstr(y, x, message, attr)
        self._stdscr.refresh()
    
    def _draw_border(self):
        padding = self._config.BORDER_PADDING
        height, width = self._stdscr.getmaxyx()
        
        y_top, y_bottom = padding, height - padding - 1
        x_left, x_right = padding, width - padding - 1
        
        attr = curses.color_pair(self.COLOR_BORDER)
        
        for x in range(x_left, x_right + 1):
            self._safe_addch(y_top, x, self._config.WALL_CHAR, attr)
            self._safe_addch(y_bottom, x, self._config.WALL_CHAR, attr)
        
        for y in range(y_top, y_bottom + 1):
            self._safe_addch(y, x_left, self._config.WALL_CHAR, attr)
            self._safe_addch(y, x_right, self._config.WALL_CHAR, attr)
    
    def _draw_hud(self, game: 'SnakeGame'):
        height, width = self._stdscr.getmaxyx()
        fps = max(1, 1000 // max(1, game.current_speed_ms))
        
        info = (
            f" Score: {game.score}  "
            f"Velocidade: {fps}fps  "
            f"Controles: ←↑↓→/WASD  (P)ausa (Q)uit "
        )
        
        if game.state == GameState.PAUSED:
            info += " [PAUSADO] "
        
        info = info[:max(0, width - 2)]
        self._safe_addstr(0, 1, info, curses.color_pair(self.COLOR_HUD))
    
    def _draw_snake(self, snake: Snake):
        attr = curses.color_pair(self.COLOR_SNAKE)
        
        for i, segment in enumerate(snake.segments):
            y, x = segment.y, segment.x
            char = (self._config.SNAKE_HEAD_CHAR if i == 0 
                    else self._config.SNAKE_BODY_CHAR)
            self._safe_addstr(y, x, char, attr)
    
    def _draw_food(self, food: Food):
        if food.position:
            y, x = food.position.y, food.position.x
            self._safe_addstr(y, x, food.char, 
                             curses.color_pair(self.COLOR_FOOD))
    
    def render_game_over(self, score: int):
        height, width = self._stdscr.getmaxyx()
        
        messages = [
            (" GAME OVER ", curses.A_BOLD),
            (f" Pontuacao: {score} ", curses.A_BOLD),
            (" Pressione R para reiniciar ou Q para sair ", curses.A_DIM),
        ]
        
        start_y = height // 2 - 1
        
        for i, (msg, attr) in enumerate(messages):
            x = (width - len(msg)) // 2
            self._safe_addstr(start_y + i, x, msg, attr)
        
        self._stdscr.refresh()
    
    def render_start_screen(self):
        messages = [
            "Jogo da Cobrinha (texto)",
            "Controles: ←↑↓→ ou WASD | (P) Pausa | (Q) Sair",
            "Pressione qualquer tecla para começar...",
        ]
        
        for i, msg in enumerate(messages):
            self._safe_addstr(2 + (i * 2), 2, msg)
        
        self._stdscr.refresh()


# =============================================================================
# SNAKE GAME FACADE
# =============================================================================
class SnakeGame:
    """Facade principal do jogo - Orquestra todos os componentes."""
    
    def __init__(self, stdscr, config: GameConfig = None):
        self._stdscr = stdscr
        self._config = config or GameConfig()
        
        self._collision_service: Optional[CollisionService] = None
        self._speed_service: Optional[SpeedService] = None
        self._input_handler: Optional[InputHandler] = None
        self._renderer: Optional[CursesRenderer] = None
        
        self._snake: Optional[Snake] = None
        self._food: Optional[Food] = None
        self._state: GameState = GameState.RUNNING
        self._score: int = 0
        self._current_speed_ms: int = self._config.INITIAL_SPEED_MS
    
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
        height, width = self._stdscr.getmaxyx()
        
        # ✅ CORREÇÃO: Criar renderer ANTES de verificar tamanho do terminal
        # Isso permite usar o renderer para mostrar mensagens de erro
        self._renderer = CursesRenderer(self._stdscr, self._config)
        self._input_handler = InputHandler(self._stdscr)
        
        # Verifica tamanho mínimo
        if height < self._config.MIN_HEIGHT or width < self._config.MIN_WIDTH:
            return False  # Renderer já está criado, pode mostrar aviso
        
        # Inicializa serviços
        self._collision_service = CollisionService(
            height, width, self._config.BORDER_PADDING
        )
        self._speed_service = SpeedService(self._config)
        
        # Inicializa entidades
        self._reset_game_state(height, width)
        
        return True
    
    def _reset_game_state(self, height: int, width: int):
        """Reseta estado do jogo para valores iniciais."""
        center_y, center_x = height // 2, width // 2
        start_position = Position(center_y, center_x)
        
        self._snake = Snake(start_position)
        self._food = Food(self._config.FOOD_CHAR)
        self._state = GameState.RUNNING
        self._score = 0
        self._current_speed_ms = self._config.INITIAL_SPEED_MS
        
        available = self._get_available_positions(height, width)
        self._food.respawn(available, self._snake.segments)
    
    def _get_available_positions(self, height: int, width: int) -> List[Position]:
        padding = self._config.BORDER_PADDING
        positions = []
        
        for y in range(padding + 1, height - padding - 1):
            for x in range(padding + 1, width - padding - 1):
                positions.append(Position(y, x))
        
        return positions
    
    def run(self):
        """Executa o loop principal do jogo."""
        height, width = self._stdscr.getmaxyx()
        
        # ✅ CORREÇÃO: Agora initialize() sempre cria o renderer
        if not self.initialize():
            # ✅ CORREÇÃO: _renderer NÃO é mais None aqui
            self._renderer.render_message(
                f"Amplie sua janela do terminal. (mínimo {self._config.MIN_WIDTH}x{self._config.MIN_HEIGHT})",
                y=1, x=1
            )
            self._renderer.render_message(
                "Pressione qualquer tecla para sair...",
                y=3, x=1
            )
            self._stdscr.nodelay(False)
            self._stdscr.getch()
            return
        
        self._renderer.render_start_screen()
        self._stdscr.nodelay(False)
        self._stdscr.getch()
        self._stdscr.nodelay(True)
        
        # Game Loop
        while self._state != GameState.QUIT:
            start_time = time.time()
            
            self._renderer.render(self)
            self._process_input()
            
            if self._state == GameState.RUNNING:
                self._update_game_logic()
            
            self._control_frame_rate(start_time)
    
    def _process_input(self):
        key = self._input_handler.get_key()
        
        if self._input_handler.is_quit_command(key):
            self._state = GameState.QUIT
            return
        
        if self._input_handler.is_pause_command(key):
            if self._state == GameState.RUNNING:
                self._state = GameState.PAUSED
            elif self._state == GameState.PAUSED:
                self._state = GameState.RUNNING
            return
        
        if self._state == GameState.GAME_OVER:
            if self._input_handler.is_restart_command(key):
                self._restart_game()
            return
        
        if self._state == GameState.RUNNING:
            direction = self._input_handler.get_direction(key)
            if direction:
                self._snake.set_direction(direction)
    
    def _update_game_logic(self):
        self._snake.move()
        
        if self._collision_service.check_any_collision(self._snake):
            self._state = GameState.GAME_OVER
            self._renderer.render_game_over(self._score)
            self._handle_game_over()
            return
        
        if self._food.is_at_position(self._snake.head):
            self._snake.grow()
            self._score += 1
            self._current_speed_ms = self._speed_service.calculate_speed(self._score)
            
            height, width = self._stdscr.getmaxyx()
            available = self._get_available_positions(height, width)
            self._food.respawn(available, self._snake.segments)
    
    def _handle_game_over(self):
        self._stdscr.nodelay(False)
        
        while True:
            key = self._stdscr.getch()
            
            if self._input_handler.is_quit_command(key):
                self._state = GameState.QUIT
                break
            
            if self._input_handler.is_restart_command(key):
                self._restart_game()
                self._stdscr.nodelay(True)
                break
    
    def _restart_game(self):
        height, width = self._stdscr.getmaxyx()
        self._reset_game_state(height, width)
        self._state = GameState.RUNNING
    
    def _control_frame_rate(self, start_time: float):
        elapsed_ms = int((time.time() - start_time) * 1000)
        remaining = self._current_speed_ms - elapsed_ms
        
        if remaining > 0:
            time.sleep(remaining / 1000.0)


# =============================================================================
# TERMINAL MANAGER
# =============================================================================
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


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    """Ponto de entrada principal."""
    with TerminalManager() as stdscr:
        game = SnakeGame(stdscr)
        game.run()


if __name__ == "__main__":
    curses.wrapper(lambda stdscr: main())