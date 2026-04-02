# Documento de Arquitetura de Software
## Snake Game - Análise Comparativa de Implementações

---

## 1. Introdução

### 1.1 Objetivo

Este documento descreve a arquitetura de software do projeto Snake Game, analisando as três implementações desenvolvidas: funcional (curses), orientada a objetos (curses) e GUI (Tkinter).

### 1.2 Escopo

O documento abrange:
- Arquitetura de cada implementação
- Padrões de projeto utilizados
- Decisões de design
- Comparação entre paradigmas (funcional vs OO)
- Extensibilidade e manutenibilidade

### 1.3 Visão Geral do Projeto

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SNAKE GAME                                    │
│                                                                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐ │
│  │  snake_text.py  │  │   oo/snake_oo.py │  │  gui/snake_oo_gui.py    │ │
│  │                 │  │                  │  │                         │ │
│  │  Paradigma:     │  │  Paradigma:      │  │  Paradigma:             │ │
│  │  FUNCIONAL      │  │  ORIENTADO A     │  │  ORIENTADO A            │ │
│  │                 │  │  OBJETOS         │  │  OBJETOS                │ │
│  │  Interface:     │  │                  │  │                         │ │
│  │  Terminal       │  │  Interface:      │  │  Interface:             │ │
│  │  (curses)       │  │  Terminal        │  │  Gráfica (GUI)          │ │
│  │                 │  │  (curses)        │  │  (Tkinter)              │ │
│  │  Linhas: ~345   │  │                  │  │                         │ │
│  │                 │  │  Linhas: ~650    │  │  Linhas: ~878           │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Arquitetura da Implementação Funcional

### 2.1 Visão Geral

A versão `snake_text.py` utiliza **programação funcional** com funções puras e estado global gerenciado através de parâmetros passados entre funções.

### 2.2 Estrutura de Módulos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        snake_text.py                                    │
│                                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │  CONSTANTES   │  │   UTILITÁRIAS │  │     TERMINAL (I/O)        │    │
│  │               │  │               │  │                           │    │
│  │  • INITIAL_*  │  │  • clamp()    │  │  • init_screen()          │    │
│  │  • MIN_*      │  │  • random_*   │  │  • end_screen()           │    │
│  │  • Direções   │  │  • opposite_* │  │  • setup_window()         │    │
│  └───────────────┘  └───────────────┘  └───────────────────────────┘    │
│          │                 │                      │                     │
│          └─────────────────┴──────────────────────┘                     │
│                              │                                          │
│          ┌───────────────────┼───────────────────────┐                  │
│          │                   │                       │                  │
│          ▼                   ▼                       ▼                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │    LÓGICA     │  │    DESENHO    │  │     CONTROLE (LOOP)       │    │
│  │               │  │               │  │                           │    │
│  │  • initial_*  │  │  • safe_*     │  │  • game_loop()            │    │
│  │  • next_dir   │  │  • draw_*     │  │  • game_step()            │    │
│  │  • move_snake │  │               │  │  • render()               │    │
│  │  • hit_*      │  │               │  │                           │    │
│  └───────────────┘  └───────────────┘  └───────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE DADOS - PROGRAMAÇÃO ESTRUTURAD              │
│                                                                         │
│  ┌──────────┐     ┌────────────┐       ┌─────────────┐     ┌──────────┐ │
│  │ TERMINAL │────▶│ INPUT HANDLER│────▶│  GAME LOGIC │────▶│ RENDERER │ │
│  │ (stdscr) │     │  getch()    │      │  move_snake │     │  draw_*  │ │
│  └──────────┘     └────────────┘       └─────────────┘     └──────────┘ │
│       ▲                                      │               │          │
│       │                                      │               │          │
│       │         ┌────────────────────────────┘               │          │
│       │         │                                            │          │
│       │         ▼                                            │          │
│       │    ┌─────────────┐                                   │          │
│       │    │   ESTADO    │                                   │          │
│       │    │ (tupla)     │                                   │          │
│       │    │             │                                   │          │
│       │    │ snake       │◀──────────────────────────────────┘          │
│       │    │ direction   │     (passado como parâmetro)                 │
│       │    │ food        │                                              │
│       │    │ score       │                                              │
│       │    │ speed_ms    │                                              │
│       │    │ paused      │                                              │
│       │    └─────────────┘                                              │
│       │                                                                 │
│       └─────────────────────────────────────────────────────────────────┘
│                        (stdscr: referência mutável)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Padrões Utilizados

| Padrão | Aplicação | Descrição |
|--------|-----------|-----------|
| **Functional Core** | Toda a lógica | Estado imutável, funções puras |
| **Pipeline** | game_step() | Processamento sequencial de dados |
| **Guard Clauses** | next_direction() | Validação no início da função |

### 2.5 Vantagens e Desvantagens

| ✅ Vantagens | ❌ Desvantagens |
|-------------|----------------|
| Código simples e direto | Estado global (tupla) passa por todas funções |
| Fácil de entender | Difícil testabilidade unitária |
| Menos código boilerplate | Reutilização limitada |
| Depuraçãoline-by-line | Acoplamento via parâmetros |

---

## 3. Arquitetura da Implementação OO (Curses)

### 3.1 Visão Geral

A versão `oo/snake_oo.py` implementa **Domain-Driven Design** com separação clara de responsabilidades e aplicação de princípios SOLID.

### 3.2 Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ARQUITETURA EM CAMADAS (oo/snake_oo.py)             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    INFRAESTRUTURA                                 │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────────────┐     │  │
│  │  │   TerminalManager   │  │       CursesRenderer            │     │  │
│  │  │   (Context Manager) │  │       (Implementação)           │     │  │
│  │  └─────────────────────┘  └─────────────────────────────────┘     │  │
│  │            │                           │                          │  │
│  │            └───────────┬───────────────┘                          │  │
│  └────────────────────────┼──────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┼──────────────────────────────────────────┐  │
│  │                        ▼                                          │  │
│  │  ┌───────────────────────────────────────────────────────────────┐│  │
│  │  │                    ABSTRAÇÕES                                 ││  │
│  │  │                                                               ││  │
│  │  │    ┌─────────────┐         ┌─────────────┐                    ││  │
│  │  │    │  Renderer   │         │InputHandler │                    ││  │
│  │  │    │  (Abstract) │         │             │                    ││  │
│  │  │    └─────────────┘         └─────────────┘                    ││  │
│  │  │                                                               ││  │
│  │  └───────────────────────────────────────────────────────────────┘│  │
│  │                           │                                       │  │
│  └───────────────────────────┼───────────────────────────────────────┘  │
│                              │                                          │
│  ┌───────────────────────────┼────────────────────────────────────────┐ │
│  │                           ▼                                        │ │
│  │  ┌───────────────────────────────────────────────────────────────┐ │ │
│  │  │                    APLICAÇÃO (Facade)                         │ │ │
│  │  │                                                               │ │ │
│  │  │    ┌─────────────────────────────────────────────────────┐    │ │ │
│  │  │    │                   SnakeGame                         │    │ │ │
│  │  │    │              (Facade Principal)                     │    │ │ │
│  │  │    │                                                     │    │ │ │
│  │  │    │  • initialize()      • run()                        │    │ │ │
│  │  │    │  • _process_input()  • _update_game_logic()         │    │ │ │
│  │  │    │  • _control_frame_rate()                            │    │ │ │
│  │  │    └─────────────────────────────────────────────────────┘    │ │ │
│  │  │                                                               │ │ │
│  │  └───────────────────────────────────────────────────────────────┘ │ │
│  │                           │                                        │ │
│  └───────────────────────────┼────────────────────────────────────────┘ │
│                              │                                          │
│  ┌───────────────────────────┼────────────────────────────────────────┐ │
│  │                           ▼                                        │ │
│  │  ┌───────────────────────────────────────────────────────────────┐ │ │
│  │  │                       DOMÍNIO                                 │ │ │
│  │  │                                                               │ │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │ │ │
│  │  │  │  Snake   │  │  Food    │  │Position  │  │GameConfig    │   │ │ │
│  │  │  │(Entity)  │  │(Entity)  │  │ (Value)  │  │ (Config)     │   │ │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │ │ │
│  │  │                                                               │ │ │
│  │  │  ┌──────────────────────┐  ┌─────────────────────┐            │ │ │
│  │  │  │  CollisionService    │  │    SpeedService     │            │ │ │
│  │  │  │  (Domain Service)    │  │    (Domain Service) │            │ │ │
│  │  │  └──────────────────────┘  └─────────────────────┘            │ │ │
│  │  │                                                               │ │ │
│  │  │  ┌──────────┐  ┌──────────┐                                   │ │ │
│  │  │  │Direction │  │GameState │                                   │ │ │
│  │  │  │  (Enum)  │  │  (Enum)  │                                   │ │ │
│  │  │  └──────────┘  └──────────┘                                   │ │ │
│  │  │                                                               │ │ │
│  │  └───────────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Diagrama de Classes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DIAGRAMA DE CLASSES                           │
│                          (oo/snake_oo.py)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  @dataclass(frozen=True)          @dataclass(frozen=True)               │
│  ┌─────────────────────┐          ┌─────────────────────┐               │
│  │     GameConfig      │          │      Position       │               │
│  ├─────────────────────┤          ├─────────────────────┤               │
│  │ INITIAL_SPEED_MS    │          │ y: int              │               │
│  │ MIN_SPEED_MS        │          │ x: int              │               │
│  │ SPEED_STEP_MS       │          ├─────────────────────┤               │
│  │ BORDER_PADDING      │          │ __add__(Direction)  │               │
│  │ MIN_HEIGHT          │          │ __iter__()          │               │
│  │ MIN_WIDTH           │          └──────────┬──────────┘               │
│  │ FOOD_CHAR           │                     │                          │
│  │ SNAKE_HEAD_CHAR     │                     │                          │
│  │ SNAKE_BODY_CHAR     │                     │                          │
│  │ WALL_CHAR           │                     │                          │
│  └─────────────────────┘                     │                          │
│                                              │                          │
│  Enum                      Enum              │ uses                     │
│  ┌─────────────────┐        ┌─────────────────────┐    ▲                │
│  │    Direction    │        │    GameState        │    │                │
│  ├─────────────────┤        ├─────────────────────┤    │                │
│  │ UP = (-1, 0)    │        │ RUNNING             │    │                │
│  │ DOWN = (1, 0)   │        │ PAUSED              │    │                │
│  │ LEFT = (0, -1)  │        │ GAME_OVER           │    │                │
│  │ RIGHT = (0, 1)  │        │ QUIT                │    │                │
│  ├─────────────────┤        └─────────────────────┘    │                │
│  │ dy, dx          │                                   │                │
│  │ is_opposite()   │                                   │                │
│  └─────────────────┘                                   │                │
│                                                        │                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         ENTIDADES                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│            │                                             ▲              │
│            │                                             │              │
│            ▼                                             │              │
│  ┌─────────────────────┐                    ┌─────────────────────┐     │
│  │       Snake         │                    │        Food         │     │
│  ├─────────────────────┤                    ├─────────────────────┤     │
│  │ -_segments: List[Pos]                    │ -_position: Position│     │
│  │ -_direction: Direction                   │ -_char: str         │     │
│  │ -_next_direction                         ├─────────────────────┤     │
│  │ -_growing: bool                          │ +position           │     │
│  ├─────────────────────┤                    │ +char               │     │
│  │ +head               │                    │ +respawn(...)       │     │
│  │ +direction          │                    │ +is_at_position()   │     │
│  │ +segments           │                    └─────────────────────┘     │
│  │ +length             │                                                │
│  │ +set_direction()    │                                                │
│  │ +move()             │                                                │
│  │ +grow()             │                                                │
│  │ +check_self_coll()  │                                                │
│  │ +occupies_position. │                                                │
│  └─────────────────────┘                                                │
│            │                                                            │
│            │ used by                                                    │
│            ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                      SERVIÇOS DE DOMÍNIO                            ││
│  └─────────────────────────────────────────────────────────────────────┘│
│            │                                             ▲              │
│            ▼                                             │              │
│  ┌─────────────────────────┐        ┌─────────────────────────┐         │
│  │    CollisionService     │        │      SpeedService       │         │
│  ├─────────────────────────┤        ├─────────────────────────┤         │
│  │ -_height: int           │        │ -_config: GameConfig    │         │
│  │ -_width: int            │        ├─────────────────────────┤         │
│  │ -_padding: int          │        │ +calculate_speed()      │         │
│  ├─────────────────────────┤        └─────────────────────────┘         │
│  │ +check_wall_collision() │                                            │
│  │ +check_self_collision() │                                            │
│  │ +check_any_collision()  │                                            │
│  └─────────────────────────┘                                            │ 
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      INFRAESTRUTURA                               │  │
│  └───────────────────────────────────────────────────────────────────   │
│            │                                           ▲                │
│            ▼                                           │                │
│  ┌─────────────────────────┐        ┌─────────────────────────┐         │
│  │     InputHandler        │        │   CursesRenderer        │         │
│  ├─────────────────────────┤        ├─────────────────────────┤         │
│  │ -_stdscr                │        │ -_stdscr                │         │
│  │ -_keymap: Dict          │        │ -_config: GameConfig    │         │
│  ├─────────────────────────┤        │ +COLOR_SNAKE            │         │
│  │ +get_key()              │        │ +COLOR_FOOD             │         │
│  │ +get_direction()        │        │ +COLOR_HUD              │         │
│  │ +is_quit_command()      │        │ +COLOR_BORDER           │         │
│  │ +is_pause_command()     │        ├─────────────────────────┤         │
│  │ +is_restart_command()   │        │ +render()               │         │
│  └─────────────────────────┘        │ +render_message()       │         │
│                                     │ +render_game_over()     │         │
│                                     │ +render_start_screen()  │         │
│                                     │ -_draw_border()         │         │
│                                     │ -_draw_hud()            │         │
│                                     │ -_draw_snake()          │         │
│                                     │ -_draw_food()           │         │
│                                     └─────────────────────────┘         │
│                                              ▲                          │
│  ┌─────────────────────────┐                  │ uses                    │
│  │     TerminalManager     │──────────────────┘                         │
│  ├─────────────────────────┤                                            │
│  │ +__enter__()            │                                            │
│  │ +__exit__()             │                                            │
│  └─────────────────────────┘                                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      FACADE (APLICAÇÃO)                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                      ▲                                  │
│                                      │                                  │
│  ┌───────────────────────────────────┴──────────────────────────────┐   │
│  │                          SnakeGame                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ -_stdscr                      -_collision_service                │   │
│  │ -_config                      -_speed_service                    │   │
│  │ -_snake                       -_input_handler                    │   │
│  │ -_food                        -_renderer                         │   │
│  │ -_state                       -_score                            │   │
│  │ -_current_speed_ms                                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ +initialize(): bool                                              │   │
│  │ +run()                                                           │   │
│  │ +snake: Snake (property)                                         │   │
│  │ +food: Food (property)                                           │   │
│  │ +state: GameState (property)                                     │   │
│  │ +score: int (property)                                           │   │
│  │ -_process_input()                                                │   │
│  │ -_update_game_logic()                                            │   │
│  │ -_handle_game_over()                                             │   │
│  │ -_restart_game()                                                 │   │
│  │ -_control_frame_rate()                                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Padrões de Projeto Utilizados

| Padrão | Classe | Benefício |
|--------|--------|-----------|
| **Facade** | SnakeGame | Interface simplificada para o cliente |
| **Strategy** | Renderer | Permite trocar renderizadores |
| **Template Method** | Renderer | Define esqueleto, subclasses implementam |
| **Context Manager** | TerminalManager | Garantia de cleanup de recursos |
| **Value Object** | Position | Imutabilidade e equality por valor |
| **Entity** | Snake, Food | Identidade e lifecycle próprio |
| **Domain Service** | CollisionService, SpeedService | Lógica que não pertence a entidades |
| **Configuration** | GameConfig | Parâmetros centralizados e imutáveis |

### 3.5 Princípios SOLID Aplicados

| Princípio | Implementação |
|-----------|---------------|
| **S - Single Responsibility** | Cada classe tem uma única responsabilidade (Snake: movimento, CollisionService: colisões) |
| **O - Open/Closed** | Renderer é abstrato; novos renderizadores podem ser adicionados sem modificar SnakeGame |
| **L - Liskov Substitution** | Qualquer Direction pode substituir outra; CursesRenderer substitui Renderer |
| **I - Interface Segregation** | Renderer tem apenas 2 métodos abstratos; InputHandler tem métodos específicos |
| **D - Dependency Inversion** | SnakeGame depende de abstrações (Renderer, CollisionService), não de implementações |

---

## 4. Arquitetura da Implementação GUI (Tkinter)

### 4.1 Visão Geral

A versão `gui/snake_oo_gui.py` estende a arquitetura OO com adaptações para o modelo event-driven do Tkinter.

### 4.2 Arquitetura com Tkinter

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ARQUITETURA GUI (gui/snake_oo_gui.py)               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      tk.Tk (ROOT)                                  │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │                      SnakeGame                               │ │ │
│  │  │                                                             │ │ │
│  │  │  ┌──────────────────────────────────────────────────────┐  │ │ │
│  │  │  │                    _setup_ui()                        │  │ │ │
│  │  │  │                                                        │  │ │ │
│  │  │  │  ┌──────────────────────────────────────────────┐   │  │ │ │
│  │  │  │  │                  tk.Frame (main_frame)       │   │  │ │ │
│  │  │  │  │                                                │   │  │ │ │
│  │  │  │  │  ┌──────────────────┐  ┌───────────────────┐ │   │  │ │ │
│  │  │  │  │  │  tk.Label (HUD)  │  │ tk.Label (Score)  │ │   │  │ │ │
│  │  │  │  │  └──────────────────┘  └───────────────────┘ │   │  │ │ │
│  │  │  │  │                                                │   │  │ │ │
│  │  │  │  │  ┌──────────────────────────────────────┐   │   │  │ │ │
│  │  │  │  │  │                                      │   │   │  │ │ │
│  │  │  │  │  │           tk.Canvas                   │   │   │  │ │ │
│  │  │  │  │  │      (Área do Jogo)                   │   │   │  │ │ │
│  │  │  │  │  │                                      │   │   │  │ │ │
│  │  │  │  │  │    ┌──────────────────────────┐     │   │   │  │ │ │
│  │  │  │  │  │    │    Snake Renderizada     │     │   │   │  │ │ │
│  │  │  │  │  │    │    ┌──┬──┬──┬──┐         │     │   │   │  │ │ │
│  │  │  │  │  │    │    │@ │o │o │o │         │     │   │   │  │ │ │
│  │  │  │  │  │    │    └──┴──┴──┴──┘         │     │   │   │  │ │ │
│  │  │  │  │  │    │         *                  │     │   │   │  │ │ │
│  │  │  │  │  │    └──────────────────────────┘     │   │   │  │ │ │
│  │  │  │  │  │                                      │   │   │  │ │ │
│  │  │  │  │  └──────────────────────────────────────┘   │   │  │ │ │
│  │  │  │  │                                                │   │  │ │ │
│  │  │  │  │  ┌──────────────────────────────────────┐   │   │  │ │ │
│  │  │  │  │  │  tk.Label (Instruções)                │   │   │  │ │ │
│  │  │  │  │  └──────────────────────────────────────┘   │   │  │ │ │
│  │  │  │  └──────────────────────────────────────────────┘   │   │  │ │
│  │  │  └──────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                     │ │
│  │  ┌────────────────────────────────────────────────────────────┐   │ │
│  │  │                   _game_loop()                                │   │ │
│  │  │                                                                    │   │ │
│  │  │      ┌──────────────────────────────────────────────┐        │   │ │
│  │  │      │  root.after(16, _game_loop)  ──────────────┼─────── │   │ │
│  │  │      │         ▲                                     │       │   │ │
│  │  │      │         │                                     │       │   │ │
│  │  │      │         └─────────────────────────────────────┘       │   │ │
│  │  │      │                (~60 FPS polling loop)                  │   │ │
│  │  │      └──────────────────────────────────────────────┘        │   │ │
│  │  │                                                                    │   │ │
│  │  └──────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │  ┌────────────────────────────────────────────────────────────┐   │ │
│  │  │                   InputHandler                               │   │ │
│  │  │                                                                    │   │ │
│  │  │      canvas.bind_all('<Key>', _on_key_press)                  │   │ │
│  │  │                   ▲                                             │   │ │
│  │  │                   │                                             │   │ │
│  │  │                   │ event.keypress                             │   │ │
│  │  │                   │                                             │   │ │
│  │  │                   └──────────────────────────────▶ callbacks  │   │ │
│  │  │                                                                     │   │ │
│  │  └──────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Comparação: Curses vs Tkinter

| Aspecto | Curses (oo/snake_oo.py) | Tkinter (gui/snake_oo_gui.py) |
|---------|-------------------------|-------------------------------|
| **Modelo** | Polling (time.sleep) | Event-driven (callbacks) |
| **Game Loop** | while + sleep | root.after() recursivo |
| **Input** | getch() no loop | bind + callbacks |
| **Render** | Redesenha tudo | Canvas.delete() + recreate |
| **FPS Control** | time.sleep() | after() scheduling |

### 4.4 Fluxo de Eventos Tkinter

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVENT LOOP - TKINTER                             │
│                                                                         │
│                    ┌─────────────────────┐                              │
│                    │   root.mainloop()   │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│           ┌───────────────────┼───────────────────┐                     │
│           │                   │                   │                     │
│           ▼                   ▼                   ▼                     │
│    ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐         │
│    │  <Key>      │   │  <FocusIn>  │   │  Timer (after)      │         │
│    │  Event      │   │  Event      │   │  Event              │         │
│    └──────┬──────┘   └─────────────┘   └──────────┬──────────┘         │
│           │                                        │                     │
│           │                                        │                     │
│           ▼                                        ▼                     │
│    ┌─────────────────────────────────────────────────────────────┐      │
│    │                   _on_key_press(event)                        │      │
│    │                                                             │      │
│    │    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │      │
│    │    │ is_quit?    │  │ is_pause?   │  │ is_restart? │     │      │
│    │    │ → _on_quit  │  │ → _on_pause │  │ → _on_restart│    │      │
│    │    └─────────────┘  └─────────────┘  └─────────────┘     │      │
│    │                                                             │      │
│    │    ┌─────────────┐                                         │      │
│    │    │ direction?   │                                         │      │
│    │    │ → callbacks │                                         │      │
│    │    │ (_on_dir)  │                                         │      │
│    │    └─────────────┘                                         │      │
│    └─────────────────────────────────────────────────────────────┘      │
│                               │                                         │
│                               │                                         │
│                               ▼                                         │
│    ┌─────────────────────────────────────────────────────────────┐      │
│    │              _game_loop() (executa ~60x/segundo)             │      │
│    │                                                             │      │
│    │    if elapsed >= current_speed_ms:                          │      │
│    │        if RUNNING:                                          │      │
│    │            _update_game_logic()  ◀── atualiza estado        │      │
│    │                                                             │      │
│    │    if RUNNING and not GAME_OVER:                            │      │
│    │        renderer.render()  ◀── redesenha canvas              │      │
│    │                                                             │      │
│    │    root.after(16, _game_loop)  ◀── agenda próxima execução  │      │
│    └─────────────────────────────────────────────────────────────┘      │
│                               │                                         │
│                               │                                         │
│                               └──────────────┐                          │
│                                              │                          │
│                                              ▼                          │
│                                    ┌─────────────────┐                  │
│                                    │  FIM (QUIT)    │                  │
│                                    └─────────────────┘                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Análise Comparativa de Implementações

### 5.1 Métricas de Código

| Métrica | snake_text.py | oo/snake_oo.py | gui/snake_oo_gui.py |
|---------|---------------|-----------------|---------------------|
| **Linhas de código** | 345 | 650 | 878 |
| **Número de funções** | 14 | 0 classes | 0 classes |
| **Número de classes** | 0 | 10 | 10 |
| **Interfaces** | N/A | 1 (Renderer) | 1 (Renderer) |
| **Enumerações** | 0 | 2 | 2 |
| **Dataclasses** | 0 | 2 | 2 |

### 5.2 Comparação de Paradigmas

| Aspecto | Funcional | OO |
|---------|-----------|-----|
| **Estado** | Tupla imutável passada via parâmetros | Objetos com estado interno |
| **Composição** | Funções chamam funções | Objetos dependem de outros objetos |
| **Extensibilidade** | Cópia e modificação de funções | Herança e composição |
| **Testabilidade** | Funções puras são facilmente testáveis | Mock de dependências |
| **Paralelismo** | Funcional puro é thread-safe | Requer sincronização |
| **Curva de aprendizado** | Menor | Maior |
| **Overhead** | Menor | Maior |

### 5.3 Trade-offs Arquiteturais

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRADE-OFFS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COMPLEXIDADE ───────────────────────────────────────────────▶          │
│     │                                                                 │
│     │     ┌───────────────────────────────────────────────────┐        │
│     │     │                                                   │        │
│     │     │         gui/snake_oo_gui.py (878 linhas)         │        │
│     │     │                                                   │        │
│     │     │    • Interface gráfica completa                  │        │
│     │     │    • Callbacks e eventos                        │        │
│     │     │    • Canvas rendering                           │        │
│     │     │    • 10 classes OO                              │        │
│     │     └───────────────────────────────────────────────────┘        │
│     │                                                                 │
│     │           ┌─────────────────────────────────────────┐           │
│     │           │                                         │           │
│     │           │      oo/snake_oo.py (650 linhas)       │           │
│     │           │                                         │           │
│     │           │    • Arquitetura SOLID completa        │           │
│     │           │    • Separação de responsabilidades    │           │
│     │           │    • 10 classes + 2 interfaces        │           │
│     │           └─────────────────────────────────────────┘           │
│     │                                                                 │
│     │                ┌─────────────────────────────┐                 │
│     │                │                             │                 │
│     │                │   snake_text.py (345 linhas)│                 │
│     │                │                             │                 │
│     │                │    • Código direto          │                 │
│     │                │    • 14 funções puras       │                 │
│     │                │    • Sem abstrações        │                 │
│     │                └─────────────────────────────┘                 │
│     │                                                                 │
│     └─────────────────────────────────────────────────────────────    │
│                                                                         │
│                                                                         │
│  REUSO ─────────────────────────────────────────────────────▶          │
│                                                                         │
│                                                                         │
│  PERFORMANCE ─────────────────────────────────────────────▶            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Decisões Arquiteturais

### 6.1 Decisão 1: Imutabilidade de GameConfig

**Problema:** Como garantir que configurações não sejam modificadas durante runtime?

**Solução:** Uso de `@dataclass(frozen=True)`

```python
@dataclass(frozen=True)
class GameConfig:
    INITIAL_SPEED_MS: int = 120
    # ...
```

**Justificativa:**
- Previne bugs por alteração acidental
- Thread-safe
- Hashable (pode ser usado como chave de dict)

### 6.2 Decisão 2: Value Object para Position

**Problema:** Como representar posições de forma segura e comparável?

**Solução:** Dataclass frozen com operador `__add__`

```python
@dataclass(frozen=True)
class Position:
    y: int
    x: int
    
    def __add__(self, direction: Direction) -> 'Position':
        return Position(self.y + direction.dy, self.x + direction.dx)
```

**Benefícios:**
- Imutável
- Comparação por valor (y, x)
- Operações matemáticas definidas

### 6.3 Decisão 3: Renderer como Interface

**Problema:** Como suportar diferentes formas de renderização?

**Solução:** Abstract Base Class com Strategy Pattern

```python
class Renderer(ABC):
    @abstractmethod
    def render(self, game_state: object) -> None: ...
    
    @abstractmethod
    def render_message(self, message: str, ...) -> None: ...
```

**Benefícios:**
- OCP: Novas renderizações sem modificar SnakeGame
- DIP: Depende de abstração, não implementação
- Testabilidade: Mock do renderer

### 6.4 Decisão 4: TerminalManager com Context Manager

**Problema:** Como garantir restauração do terminal mesmo com exceções?

**Solução:** RAII pattern via context manager

```python
class TerminalManager:
    def __enter__(self):
        curses.initscr()
        return self._stdscr
    
    def __exit__(self, ...):
        curses.endwin()  # Sempre executa
```

**Benefício:** Garantia de cleanup (defesa em profundidade)

### 6.5 Decisão 5: Game Loop com Callbacks (Tkinter)

**Problema:** Como integrar game loop imperativo com event-driven framework?

**Solução:** Callbacks para input, polling via after()

```python
# Input via callbacks
self._canvas.bind_all('<Key>', self._on_key_press)

# Game loop via polling
self._game_loop_id = self._root.after(16, self._game_loop)
```

---

## 7. Extensibilidade

### 7.1 Adicionar Novo Renderizador

Para adicionar um renderizador web (exemplo):

```python
class WebRenderer(Renderer):
    def __init__(self, websocket):
        self._ws = websocket
    
    def render(self, game):
        # Envia estado para cliente via WebSocket
        self._ws.send(game.to_json())
    
    def render_message(self, title, subtitle, instructions):
        # Envia mensagem para cliente
        self._ws.send(json.dumps({
            'type': 'message',
            'title': title,
            'subtitle': subtitle
        }))
```

### 7.2 Adicionar Novo Serviço

```python
class ScoreService:
    """Serviço para gerenciar pontuação e achievements."""
    
    def __init__(self, storage):
        self._storage = storage
    
    def add_score(self, points):
        self._current += points
        self._check_achievements()
    
    def get_high_score(self):
        return self._storage.load()
```

### 7.3 Adicionar Power-ups

```python
@dataclass(frozen=True)
class PowerUp:
    position: Position
    effect: PowerUpEffect
    duration_ms: int

class PowerUpManager:
    def __init__(self):
        self._active_powerups: List[PowerUp] = []
    
    def spawn(self, available_positions):
        # Lógica de spawn
```

---

## 8. Considerações de Deployment

### 8.1 Dependências

| Implementação | Dependências |
|--------------|--------------|
| snake_text.py | Python 3.8+, curses (stdlib) |
| oo/snake_oo.py | Python 3.8+, curses (stdlib) |
| gui/snake_oo_gui.py | Python 3.8+, tkinter (stdlib) |

### 8.2 Ambiente de Execução

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AMBIENTE DE EXECUÇÃO                             │
│                                                                         │
│  snake_text.py / oo/snake_oo.py:                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │   │
│  │    │   Linux     │      │   macOS     │      │   WSL       │  │   │
│  │    │  (curses)   │      │  (ncurses)  │      │  (curses)   │  │   │
│  │    └─────────────┘      └─────────────┘      └─────────────┘  │   │
│  │                                                                  │   │
│  │    ┌─────────────────────────────────────────────────────────┐  │   │
│  │    │              Terminal Emulator                            │  │   │
│  │    │    (gnome-terminal, iTerm2, Windows Terminal)            │  │   │
│  │    └─────────────────────────────────────────────────────────┘  │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  gui/snake_oo_gui.py:                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │   │
│  │    │   Linux     │      │   macOS     │      │   Windows   │  │   │
│  │    │  (Tkinter) │      │  (Tkinter)  │      │  (Tkinter)  │  │   │
│  │    └─────────────┘      └─────────────┘      └─────────────┘  │   │
│  │                                                                  │   │
│  │    tkinter default no Python, não requer instalação adicional │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Testabilidade

### 9.1 Testes Unitários (Exemplo)

```python
# test_snake_oo.py
import pytest
from oo.snake_oo import Snake, Position, Direction

class TestSnake:
    def test_move_forward(self):
        snake = Snake(Position(5, 5))
        initial_length = snake.length
        
        snake.set_direction(Direction.RIGHT)
        snake.move()
        
        assert snake.length == initial_length
        assert snake.head == Position(5, 6)
    
    def test_grow(self):
        snake = Snake(Position(5, 5))
        initial_length = snake.length
        
        snake.grow()
        snake.move()
        
        assert snake.length == initial_length + 1
    
    def test_no_reverse_direction(self):
        snake = Snake(Position(5, 5), initial_direction=Direction.RIGHT)
        
        result = snake.set_direction(Direction.LEFT)  # Oposta
        
        assert result is False
        assert snake.direction == Direction.RIGHT

class TestCollisionService:
    def test_wall_collision(self):
        service = CollisionService(20, 40)
        
        assert service.check_wall_collision(Position(0, 20)) is True
        assert service.check_wall_collision(Position(10, 20)) is False
```

### 9.2 Testabilidade por Implementação

| Aspecto | Funcional | OO |
|---------|-----------|-----|
| Testar lógica pura | Fácil (funções puras) | Médio (mock dependencies) |
| Testar renderização | Difícil (efetos colaterais) | Médio (mock renderer) |
| Testar integração | Médio | Fácil (injeção de dependências) |

---

## 10. Conclusão

### 10.1 Resumo das Arquiteturas

| Implementação | Paradigma | Arquitetura | Complexidade |
|--------------|-----------|-------------|--------------|
| snake_text.py | Funcional | Monolítica | Baixa |
| oo/snake_oo.py | OO | DDD + SOLID | Média |
| gui/snake_oo_gui.py | OO | DDD + Event-driven | Alta |

### 10.2 Recomendações de Uso

| Cenário | Recomendação |
|---------|-------------|
| Protótipo rápido | snake_text.py |
| Aprendizado de Python | snake_text.py |
| Projeto acadêmico | oo/snake_oo.py |
| Multi-plataforma | gui/snake_oo_gui.py |
| Código production-ready | oo/snake_oo.py ou gui/snake_oo_gui.py |

### 10.3 Lições Aprendidas

1. **Programação Funcional** é excelente para lógica simples e direta
2. **OO com SOLID** escala melhor para sistemas complexos
3. **Value Objects** (Position) previnem bugs com imutabilidade
4. **Facades** simplificam a interface com sistemas complexos
5. **Context Managers** garantem cleanup de recursos
6. **Interfaces abstratas** permitem extensibilidade sem modificação

---

*Documento de Arquitetura de Software - Snake Game*
*Versão 1.0 - 2026*
