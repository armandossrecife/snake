# Documento de Requisitos de Software
## Jogo da Cobrinha (Snake Game)

---

## 1. Introdução

### 1.1 Objetivo do Documento

Este documento especifica os requisitos funcionais e não funcionais para o desenvolvimento do jogo "Snake Game", uma implementação do clássico jogo da cobrinha.

### 1.2 Escopo do Projeto

O projeto consiste em três implementações do mesmo jogo:
- **snake_text.py**: Versão terminal usando curses (Linux/macOS)
- **oo/snake_oo.py**: Versão orientada a objetos usando curses
- **gui/snake_oo_gui.py**: Versão com interface gráfica usando Tkinter (multiplataforma)

### 1.3 Definições e Abreviações

| Termo | Definição |
|-------|-----------|
| **Snake** | Entidade controlável pelo jogador que se move pelo tabuleiro |
| **Food** | Item coletável que aumenta o tamanho da cobra |
| **Score** | Pontuação obtida pela coleta de comida |
| **Game Loop** | Ciclo principal que atualiza e renderiza o jogo |
| **FPS** | Frames por segundo - velocidade de atualização da tela |
| **HUD** | Heads-Up Display - informações exibidas durante o jogo |
| **Curses** | Biblioteca Python para manipulação de terminal |
| **Tkinter** | Biblioteca Python para interfaces gráficas |

---

## 2. Requisitos Funcionais

### 2.1 Controle da Cobra

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-01 | Movimento Direcional | Obrigatório | A cobra deve se mover nas quatro direções cardinais (cima, baixo, esquerda, direita) |
| RF-02 | Controles de Teclado | Obrigatório | O jogador deve poder controlar a cobra usando setas direcionais (↑↓←→) |
| RF-03 | Controles Alternativos | Desejável | O jogador deve poder controlar a cobra usando teclas WASD |
| RF-04 | Bloqueio de Reversão | Obrigatório | A cobra não deve poder mudar diretamente para direção oposta (ex: de RIGHT para LEFT) |
| RF-05 | Movimento Contínuo | Obrigatório | A cobra deve se mover continuamente na direção atual |

### 2.2 Sistema de Coleta (Comida)

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-06 | Geração de Comida | Obrigatório | Uma comida deve aparecer aleatoriamente no tabuleiro |
| RF-07 | Posicionamento Válido | Obrigatório | A comida nunca deve aparecer sobre a cobra |
| RF-08 | Respawn Automático | Obrigatório | Após coletada, nova comida deve aparecer em posição válida |
| RF-09 | Crescimento da Cobra | Obrigatório | Ao coletar comida, a cobra deve aumentar em exatamente 1 segmento |
| RF-10 | Incremento de Pontuação | Obrigatório | Cada comida coletada deve incrementar a pontuação em 1 ponto |

### 2.3 Sistema de Colisão

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-11 | Colisão com Parede | Obrigatório | O jogo deve terminar quando a cobra colidir com a borda do tabuleiro |
| RF-12 | Colisão com Corpo | Obrigatório | O jogo deve terminar quando a cobra colidir consigo mesma |
| RF-13 | Tolerância a Múltiplas Teclas | Desejável | O sistema deve ignorar comandos de direção intermediários para evitar mudanças rápidas demais |

### 2.4 Sistema de Velocidade

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-14 | Velocidade Inicial | Obrigatório | O jogo deve iniciar com velocidade de ~120ms por frame (~8 FPS) |
| RF-15 | Aceleração Progresiva | Obrigatório | A velocidade deve aumentar progressivamente conforme o score |
| RF-16 | Limite de Velocidade | Obrigatório | Deve haver um limite máximo de velocidade (mínimo 50ms por frame) |
| RF-17 | Velocidade Configurável | Desejável | A velocidade inicial deve ser configurável via constantes |

### 2.5 Estados do Jogo

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-18 | Estado RUNNING | Obrigatório | O jogo deve permitir movimento e coleta quando ativo |
| RF-19 | Estado PAUSED | Obrigatório | O jogador deve poder pausar o jogo |
| RF-20 | Estado GAME_OVER | Obrigatório | O jogo deve exibir tela de fim quando terminar |
| RF-21 | Reinício do Jogo | Obrigatório | O jogador deve poder reiniciar após game over |

### 2.6 Interface com o Usuário

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-22 | Exibição de Score | Obrigatório | O score atual deve ser exibido durante o jogo |
| RF-23 | Exibição de Velocidade | Desejável | A velocidade atual (em FPS) deve ser exibida |
| RF-24 | Tela de Boas-Vindas | Desejável | O jogo deve exibir instruções iniciais antes de iniciar |
| RF-25 | Tela de Game Over | Obrigatório | Deve exibir pontuação final e opção de reinício |
| RF-26 | Comandos Visualizados | Desejável | Os controles disponíveis devem ser exibidos na tela |

### 2.7 Controles do Jogo

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| RF-27 | Tecla Pausar | Obrigatório | Tecla 'P' deve pausar/retomar o jogo |
| RF-28 | Tecla Sair | Obrigatório | Tecla 'Q' deve encerrar o jogo |
| RF-29 | Tecla Reiniciar | Obrigatório | Tecla 'R' deve reiniciar após game over |
| RF-30 | Input Não-Bloqueante | Obrigatório | O jogo não deve travar esperando entrada do teclado |

---

## 3. Requisitos Não Funcionais

### 3.1 Performance

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-01 | Tempo de Resposta | ≤ 16ms | Input deve ser processado em menos de um frame (~60 FPS input) |
| RNF-02 | Uso de CPU | < 5% | Jogo ocioso não deve consumir recursos significativos |
| RNF-03 | Memória | < 50MB | Consumo máximo de memória durante execução |
| RNF-04 | Inicialização | ≤ 2s | Tempo para primeira renderização do jogo |

### 3.2 Compatibilidade

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-05 | Python | 3.8+ | Deve funcionar em Python 3.8 ou superior |
| RNF-06 | SO - Curses | Linux/macOS | Versão curses funciona em sistemas POSIX |
| RNF-07 | SO - GUI | Multiplataforma | Versão GUI funciona em Windows, Linux e macOS |
| RNF-08 | Dependências | stdlib | Deve usar apenas bibliotecas padrão quando possível |

### 3.3 Usabilidade

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-09 | Curva de Aprendizado | ≤ 1min | Jogador deve entender controles imediatamente |
| RNF-10 | Feedback Visual | Imediato | Toda ação do jogador deve ter feedback visual instantâneo |
| RNF-11 | Estados Claros | N/A | Estados do jogo (RUNNING/PAUSED/GAME_OVER) devem ser claramente indicados |
| RNF-12 | Tamanho Mínimo Terminal | 40x20 | Versão curses deve funcionar em terminais ≥ 40x20 caracteres |

### 3.4 Confiabilidade

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-13 | Tratamento de Erros | N/A | Erros de renderização devem ser capturados sem crash |
| RNF-14 | Restauração de Terminal | 100% | Terminal deve ser restaurado mesmo em caso de erro |
| RNF-15 | Redimensionamento | N/A | Sistema deve lidar graciosamente com redimensionamento |
| RNF-16 | Caracteres ASCII | N/A | Versão curses deve usar apenas ASCII para compatibilidade |

### 3.5 Manutenibilidade

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-17 | Código Modular | N/A | Funções/classes devem ter responsabilidade única |
| RNF-18 | Documentação | N/A | Código deve conter docstrings e documentação |
| RNF-19 | Type Hints | Desejável | Uso de type hints para melhor legibilidade |
| RNF-20 | Configurações Centralizadas | N/A | Constantes de configuração em local único |

### 3.6 Portabilidade (Versão GUI)

| ID | Requisito | Critério | Descrição |
|----|-----------|----------|-----------|
| RNF-21 | Resolução | ≥ 800x600 | Deve funcionar em resoluções típicas |
| RNF-22 | Janela Redimensionável | Opcional | Janela pode ou não ser redimensionável |
| RNF-23 | Centralização | N/A | Janela deve iniciar centralizada na tela |

---

## 4. Requisitos de Interface

### 4.1 Interface de Terminal (Curses)

| Elemento | Caractere | Cor |
|----------|-----------|-----|
| Cabeça da Cobra | `@` | Verde |
| Corpo da Cobra | `o` | Verde |
| Comida | `*` | Vermelho |
| Parede/Borda | `#` | Branco |
| HUD | Texto | Ciano |

### 4.2 Interface Gráfica (Tkinter)

| Elemento | Forma | Cor |
|----------|-------|-----|
| Cabeça da Cobra | Retângulo com olhos | Verde claro (#00ff88) |
| Corpo da Cobra | Retângulo | Verde escuro (#00cc66) |
| Comida | Círculo | Vermelho (#ff4444) |
| Borda | Retângulo | Cinza (#444466) |
| Fundo | N/A | Azul escuro (#1a1a2e) |

---

## 5. Requisitos de Configuração Padrão

| Parâmetro | Valor Padrão | Descrição |
|-----------|--------------|-----------|
| `INITIAL_SPEED_MS` | 120 | Velocidade inicial (ms/frame) |
| `MIN_SPEED_MS` | 50 | Velocidade máxima (limite) |
| `SPEED_STEP_MS` | 3 | Redução de ms por ponto |
| `BORDER_PADDING` | 1 | Margem da borda em células |
| `BOARD_WIDTH_CELLS` | 40 | Largura do tabuleiro (GUI) |
| `BOARD_HEIGHT_CELLS` | 30 | Altura do tabuleiro (GUI) |
| `CELL_SIZE` | 15 | Tamanho da célula em pixels (GUI) |

---

## 6. Matriz de Rastreabilidade

### 6.1 RF × Implementação

| Requisito | snake_text.py | oo/snake_oo.py | gui/snake_oo_gui.py |
|-----------|---------------|-----------------|---------------------|
| RF-01 | ✓ | ✓ | ✓ |
| RF-02 | ✓ | ✓ | ✓ |
| RF-03 | ✓ | ✓ | ✓ |
| RF-04 | ✓ | ✓ | ✓ |
| RF-05 | ✓ | ✓ | ✓ |
| RF-06 | ✓ | ✓ | ✓ |
| RF-07 | ✓ | ✓ | ✓ |
| RF-08 | ✓ | ✓ | ✓ |
| RF-09 | ✓ | ✓ | ✓ |
| RF-10 | ✓ | ✓ | ✓ |
| RF-11 | ✓ | ✓ | ✓ |
| RF-12 | ✓ | ✓ | ✓ |
| RF-13 | ✗ | ✗ | ✗ |
| RF-14 | ✓ | ✓ | ✓ |
| RF-15 | ✓ | ✓ | ✓ |
| RF-16 | ✓ | ✓ | ✓ |
| RF-17 | ✓ | ✓ | ✓ |
| RF-18 | ✓ | ✓ | ✓ |
| RF-19 | ✓ | ✓ | ✓ |
| RF-20 | ✓ | ✓ | ✓ |
| RF-21 | ✓ | ✓ | ✓ |
| RF-22 | ✓ | ✓ | ✓ |
| RF-23 | ✓ | ✓ | ✓ |
| RF-24 | ✓ | ✓ | ✓ |
| RF-25 | ✓ | ✓ | ✓ |
| RF-26 | ✓ | ✓ | ✓ |
| RF-27 | ✓ | ✓ | ✓ |
| RF-28 | ✓ | ✓ | ✓ |
| RF-29 | ✓ | ✓ | ✓ |
| RF-30 | ✓ | ✓ | ✓ |

---

## 7. Casos de Uso

### 7.1 UC-01: Iniciar Jogo
1. Jogador executa o programa
2. Sistema exibe tela de boas-vindas
3. Jogador pressiona qualquer tecla
4. Sistema inicia o jogo com cobra no centro

### 7.2 UC-02: Mover Cobra
1. Sistema aguarda entrada do jogador
2. Jogador pressiona tecla de direção
3. Sistema valida direção (não é oposta)
4. Sistema atualiza direção da cobra
5. Na próxima iteração, cobra se move

### 7.3 UC-03: Coletar Comida
1. Cobra se move para posição da comida
2. Sistema detecta colisão cobra-comida
3. Sistema incrementa score
4. Sistema aumenta tamanho da cobra
5. Sistema reposiciona comida em local válido
6. Sistema ajusta velocidade

### 7.4 UC-04: Pausar Jogo
1. Jogador pressiona 'P'
2. Sistema interrompe atualização do jogo
3. Sistema exibe indicador "PAUSADO"
4. Jogador pressiona 'P' novamente
5. Sistema retoma jogo mantendo estado

### 7.5 UC-05: Game Over
1. Sistema detecta colisão (parede ou corpo)
2. Sistema exibe tela de game over
3. Sistema aguarda decisão do jogador
4. Se 'R': sistema reinicia jogo (UC-01)
5. Se 'Q': sistema encerra programa

---

## 8. Critérios de Aceite

### 8.1 Aceite Global

- [ ] Jogo inicia sem erros em todas as plataformas suportadas
- [ ] Cobra responde a todos os controles especificados
- [ ] Colisão com parede/corpo encerra jogo corretamente
- [ ] Score incrementa corretamente ao coletar comida
- [ ] Velocidade aumenta conforme pontuação
- [ ] Terminal é restaurado após encerramento

### 8.2 Aceite snake_text.py

- [ ] Funciona em terminal Linux/macOS
- [ ] Usa apenas caracteres ASCII
- [ ] Não crasha com coordenadas inválidas
- [ ] Responde a setas e WASD

### 8.3 Aceite oo/snake_oo.py

- [ ] Implementação orientada a objetos completa
- [ ] Separação clara de responsabilidades
- [ ] Princípios SOLID aplicados

### 8.4 Aceite gui/snake_oo_gui.py

- [ ] Interface gráfica responsiva
- [ ] Cobra desenhada com olhos direcionais
- [ ] Funciona em Windows, Linux e macOS

---

## 9. Restrições

| ID | Restrição | Descrição |
|----|-----------|-----------|
| RES-01 | Unicode | Versão curses não suporta caracteres unicode |
| RES-02 | Terminal | Versão curses requer terminal compatible com ncurses |
| RES-03 | Performance | Não é adequado para jogos que requerem >30 FPS |

---

## 10. Histórico de Versões

| Versão | Data | Descrição |
|--------|------|-----------|
| 1.0 | 2026-03-30 | Versão inicial do documento |

---

*Documento de Requisitos - Snake Game*
