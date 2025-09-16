# Jogo da cobrinha em modo texto

## Sobre o jogo

Mais detalhes sobre o jogo da serpente neste [link](https://pt.wikipedia.org/wiki/Serpente_(jogo_eletrônico))

Este programa usa **somente caracteres ASCII** (parede `#`, comida `*`, cabeça `@`, corpo `o`).

## Como rodar

Baixe o arquivo `snake_text.py` para um diretório local da sua máquina.

Como rodar:

```bash
python3 snake_text.py
```

Se der algum problema:

* Experimente redimensionar o terminal para ficar maior (mín. \~40x20).
* Garanta que está usando o Python3 do sistema com `curses` funcional: `python3 -V`.
* Rodar pelo Terminal.

## Detalhes da implementação 

O arquivo snake_text.py implementa o clássico jogo da cobrinha (Snake) para o terminal, usando a biblioteca `curses` para manipulação de tela e teclado.  

A biblioteca [curses](https://docs.python.org/pt-br/3.10/howto/curses.html) só funciona em ambiente POSIX (Linux ou MacOS), ou seja, esta versão não funciona no Windows.

Logo abaixo segue um resumo das principais partes do código:

### 1. **Configurações e Constantes**
Define velocidade inicial, caracteres ASCII para cobra, comida e borda, além das direções possíveis (cima, baixo, esquerda, direita).

### 2. **Funções Utilitárias**
- `clamp`: limita valores dentro de um intervalo.
- `random_empty_cell`: escolhe uma célula livre para posicionar a comida.
- `opposite_dir`: verifica se duas direções são opostas.

### 3. **Inicialização do Terminal**
- `init_screen` e `end_screen`: configuram e restauram o terminal para uso com curses.


### 4. **Desenho na Tela**
- `setup_window`: configura cores e modo de leitura.
- `safe_addstr` e `safe_addch`: escrevem caracteres na tela, ignorando erros.
- `draw_border`, `draw_hud`, `draw_snake_and_food`: desenham borda, placar, cobra e comida.

### 5. **Lógica do Jogo**
- `initial_state`: cria o estado inicial do jogo.
- `next_direction`: converte teclas pressionadas em direções.
- `move_snake`, `grow_snake`: movimentam e aumentam a cobra.
- `hit_wall_or_self`: detecta colisão com parede ou corpo.
- `adjust_speed`: acelera o jogo conforme a cobra cresce.
- `game_step`: executa um passo do jogo (movimento, colisão, comer, pausa, etc).

### 6. **Renderização e Game Over**
- `render`: atualiza a tela com o estado atual.
- `game_over_screen`: mostra mensagem de fim de jogo.
- `wait_restart_or_quit`: espera o jogador decidir reiniciar ou sair.

### 7. **Loop Principal**
- `game_loop`: controla o fluxo do jogo, incluindo início, reinício, pausa, fim e controle de tempo.

### 8. **Função Principal**
- `main`: inicializa o terminal, executa o loop do jogo e restaura o terminal ao final.

### 9. **Execução**
- Usa `curses.wrapper` para garantir que o terminal seja restaurado corretamente após o jogo.

O código é funcional (sem classes), organizado em funções, e permite jogar Snake no terminal usando setas ou WASD, com pausa, reinício e ajuste automático de velocidade.

# Análise de Código

## Leitura sequencial e marcação (análise estática)

**1) Variáveis**

* a) Exemplos de constantes/configurações:

  * `INITIAL_SPEED = 120` → velocidade inicial em ms por frame.
  * `MIN_SPEED = 50` → limite mínimo de velocidade (cobra mais rápida).
  * `SPEED_STEP = 3` → quanto diminui o tempo por frame a cada ponto.
  * `BORDER_PADDING = 1` → margem para desenhar a borda.
  * `FOOD_CHAR = "*"` → caractere usado para a comida.
* b) Estado inicial (`initial_state`):

  * `snake` (lista de tuplas) → guarda as posições dos segmentos.
  * `direction` (tupla) → direção atual da cobra (ex.: `RIGHT`).
  * `score` (int) → pontuação do jogador.

**2) Expressões e Operadores**

* a) Aritméticas:

  * `height // 2` → encontra o meio da tela.
  * `1000 // max(1, speed_ms)` → calcula FPS aproximado.
  * `INITIAL_SPEED - score * SPEED_STEP` → ajusta velocidade conforme o placar.
* b) Relacionais/lógicos:

  * `if y <= BORDER_PADDING` → testa se bateu na parede.
  * `if head in snake[1:]` → testa colisão com o corpo.
  * `if not paused:` → verifica estado de pausa.
* c) Operador de pertencimento: `(y, x) not in snake` em `random_empty_cell` → garante que a comida não aparece dentro da cobra.

**3) Controle de Fluxo**

* a) Condicionais:

  * `if key in (ord('q'), ord('Q')):` → encerra o jogo.
  * `if ate:` → decide se deve crescer e somar pontos.
* b) Laços:

  * `for x in range(x0, x1 + 1):` → desenha a borda superior/inferior.
  * `while True:` em `game_loop` → mantém o jogo rodando até sair.
* c) `try/except`:

  * Em `safe_addstr`, captura `curses.error` para evitar crash se tentar desenhar fora da tela.

**4) Tipos em Python**

* a) **Lista**: `snake = [(cy, cx), (cy, cx-1), (cy, cx-2)]`. Crescer = `snake + [snake[-1]]`.
* b) **Tupla**: direções (`UP = (-1,0)`) e posições (`(y,x)`). São imutáveis, adequadas para coordenadas.
* c) **Dicionário**: `keymap` em `next_direction` → mapeia teclas para vetores direção.
* d) **Set**: não foi usado, mas poderia acelerar a checagem `if head in snake[1:]`.
* e) **Strings**: caracteres de interface (`"#"`, `"o"`, `"@"`, `"*"`) para representar elementos.

**5) Funções**

* a) Lógica: `move_snake`, `grow_snake`, `hit_wall_or_self`, `adjust_speed`.
  Visual/I/O: `draw_border`, `draw_hud`, `draw_snake_and_food`, `render`.
  → Boa separação: lógica pode ser testada isoladamente.
* b) Exemplo:

  * `move_snake(snake, direction)` recebe lista e direção, retorna nova lista com a cabeça movida.
  * `adjust_speed(speed_ms, score)` recebe velocidade e pontuação, retorna velocidade ajustada.

**6) Uso de bibliotecas**

* `curses` → desenhar na tela do terminal e capturar teclas sem travar.
* `random` → sortear posição da comida.
* `time` → controlar temporização entre frames (`sleep`).
* Limitação macOS: `curses` não lida bem com caracteres Unicode → solução foi usar apenas ASCII (`*`, `#`, `o`, `@`).

## Execução e observação

1. Durante o jogo:

* A pontuação aumenta quando a cobra come (`score += 1`).
* A velocidade aumenta porque `speed_ms` diminui a cada ponto (`adjust_speed`).
* Colisão com parede ou corpo finaliza a partida (`game_over_screen`).

2. Com `paused = True`:

* O loop ainda desenha a tela e aceita tecla `P`/`Q`.
* Mas a lógica de `move_snake`, `grow_snake` e colisões não é executada.

## Pequenas modificações que podem ser feitas

1. **Wrap nas bordas**:
   Substituir colisão por:

```python
y = (head_y + dy) % height
x = (head_x + dx) % width
new_head = (y, x)
```

Agora a cobra atravessa e aparece do outro lado.

2. **Colisão com set**:

```python
snake_set = set(snake)
if head in snake_set:
    return True
```

Busca O(1) em vez de O(n).

3. **Comida especial**:
   Adicionar contador de comidas:

```python
if ate:
    if score % 5 == 0:
        # comida especial
        score += 3
    else:
        score += 1
```

Comida especial dá mais pontos e não acelera.
