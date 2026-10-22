# Formação e saque — versão 9

Atualização para partidas Solo, com teste no headset ainda necessário.

- 2v2: o aliado não escolhe bloqueio contra bolas adversárias. Ainda pode saltar para atacar um levantamento do próprio time.
- Saque humano: a bola aguarda congelada e escondida. Ao pedir para agarrar com qualquer mão, ela aparece no centro dessa mão. A rotina original mantém a bola presa enquanto o botão está segurado e lança ao soltar. Funciona com o gatilho; o comando alternativo de agarrar do jogo também continua aceito.
- 4v4: posição de fundo central, duas pontas e levantador central próximo à rede nos dois times. A rotação original percorre as quatro funções, sem a restrição de ficar somente na frente durante essa partida.
- Quem ocupa o fundo recebe multiplicador de movimento de 1,60, tanto bot quanto humano. Ao sair dessa posição, retorna à velocidade normal.
- Bots fazem recepção para o levantador e levantamento para uma ponta, com ataque no terceiro toque. Se o levantador fizer a própria recepção, há uma alternativa para evitar dois toques seguidos do mesmo jogador. O jogador humano continua controlando seus próprios passes.
- O modo online não recebe a formação nova nem o novo saque na mão.

Implementação em `mode_2v2.c` e `formation_serve.c`, incorporada em GameAssembly.dll pelo build_patch.py. A versão anterior completa do binário está em `versions/v8-antes-formacao`.

Validação: testes de código nativo compilado nos dois endereços de carregamento, geometria, rotação de funções, velocidade, escolha de recebedores, comportamento do aliado e fluxo original Hand.Update/StartInteraction para ambas as mãos. Os testes simulam os serviços da Unity e não substituem uma partida em VR.
