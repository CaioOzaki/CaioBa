# Modo Solo 2v2

Abra Volleyball Fever normalmente pela Steam. No menu, escolha **Solo > 2v2** e depois **Beach Day** (areia de dia) ou **Indoor**. Solo > 4v4 mantém as quatro opções anteriores. Voltar retorna à escolha do formato; voltar novamente retorna ao menu principal.

O 2v2 é solo: você e um bot contra dois bots. A movimentação do jogador e dos bots usa um multiplicador de 1,40. O valor salvo nas configurações não é alterado. Levantamentos dos bots direcionados ao jogador recebem 1,25 m adicionais na altura do arco. Ataques e passes entre bots continuam com seus parâmetros anteriores.

As duas posições de cada equipe cobrem a profundidade da quadra e alternam o saque num ciclo de duas posições. A geometria original é restaurada ao iniciar 4v4. O modo online, o modo bomba e novos jogos iniciados pelo menu principal não herdam o formato 2v2.

Mantidas a textura da bola e a física otimizada v2. O patch é específico do build Steam 9216628 (Unity 2019.4.5f1).

## Verificação

### Ajuste de recepção e construção da jogada

No 2v2, a assistência de mira original do jogo fica disponível apenas para a recepção direta de um saque adversário. O primeiro contato válido da equipe encerra essa assistência, seja do jogador ou do bot. Saques do próprio time e os demais contatos do rally ficam sem assistência. Isso não altera a preferência salva nem o comportamento do 4v4.

O bot aliado prepara um passe/levantamento nos dois primeiros toques da equipe, e pode devolver no terceiro. Os saques do bot e a estratégia dos adversários permanecem como antes. O jogador continua livre para direcionar a própria bola; esta alteração controla a decisão do bot, não força três contatos quando o jogador devolve antes.

20 verificações adicionais passaram em código nativo emulado, incluindo consumo da recepção, colisões rejeitadas, primeiro/segundo/terceiro toque, adversários e restauração dos parâmetros. Falta testar esses ajustes de jogabilidade no Quest 3.

A versão anterior do 2v2 foi confirmada pelo usuário como funcional, incluindo o menu, e está preservada em `versions/v3-confirmado`. O backup completo anterior ao 2v2 permanece na Área de Trabalho.

- 18 grupos de testes do código nativo do 2v2, com endereços normais e relocados: menu, criação de três bots, posições, rotação, cobertura, velocidades, levantamentos e restauração de 4v4.
- 9 testes da integração da física e 10 testes dos cálculos da física aprovados.
- Inicialização de uma cópia de diagnóstico no Unity sem headset: carregou o ambiente IndoorArenaScene sem erros registrados. O menu VR ficou inativo, portanto esse teste não confirma uma partida completa.
- A conferência visual, o FPS no Quest 3 e a sensação dos levantamentos precisam ser avaliados jogando em VR.

Os testes nativos usam simulação das chamadas do motor; não são uma sessão real de VR. A versão instalada não inclui os comandos temporários de diagnóstico.

## Retornar à versão estável anterior

Backup completo, criado antes do 2v2 e conferido por hash:

`C:\Users\Usuario\Desktop\VolleyballFever_BACKUP_estavel_antes_2v2_2026-10-21_21-44-10.zip`

Com o jogo fechado, extraia o ZIP e execute o RESTAURAR.cmd que está dentro dele. Esse backup inclui as melhorias anteriores. O comando Restaurar-original.cmd deste pacote retorna aos arquivos originais do jogo, sem essas melhorias.

Fontes: mode_2v2.c e spin_mod.c. Montagem do arquivo: build_patch.py. Testes: test_2v2.py, test_hooks.py e test_physics.py. Fontes de referência em sources/ não foram alteradas.

## Ajuste de tempo para sacar
No 2v2, a bola aparece 2 m mais alta no início dos saques dos bots de ambos os times. A posição da quadra e o saque humano não mudam. O aliado usa agora multiplicador 1,60 de velocidade (aproximadamente 14,3% a mais que o 1,40 anterior); adversários e jogador mantêm 1,40. Os testes verificam altura sem acumulação, posições preservadas, velocidade por equipe e comportamento do 4v4. A confirmação de que os saques perdidos foram eliminados depende de jogar em VR. A versão anterior está preservada em versions/v4-confirmado.


## Espera antes do saque — 2v2 e 4v4
Acrescentados 3 segundos antes de a bola aparecer nos saques dos bots, após qualquer rotação. A pausa usa WaitForSeconds do Unity e não bloqueia a movimentação. Aplica-se ao fluxo de saque controlado pelo anfitrião nos dois formatos. Saques humanos e modo bomba mantêm o tempo anterior. Altura da bola, velocidade do aliado e assistência de recepção permanecem como na versão anterior. Testes nativos conferiram pausa única, posição da espera após rotação e continuação correta do saque. O resultado prático ainda precisa ser testado em VR. Versão anterior preservada em versions/v5-antes-espera.

