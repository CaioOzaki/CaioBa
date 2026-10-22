# Volleyball Fever: Mikasa Beach Pro e giro por raspada

Pacote experimental pessoal para a instalação Steam em `C:\APPS\STEAM\steamapps\common\Volleyball`, build 9216628, Unity 2019.4.5f1 IL2CPP x64. Preparado em 21/10/2026. Não redistribuir os arquivos proprietários incluídos na cópia local.

## Revisão 2: desempenho

Após o relato de aproximadamente 10 FPS, a primeira versão foi retirada para comparação. O usuário ainda não mediu o FPS sem ela, portanto não foi estabelecido que o mod causou a queda.

A revisão 2 mantém a transferência de giro no impacto e o efeito Magnus. A integração adicional ocorre até 30 vezes por segundo, acumula o tempo entre quadros e usa passos internos limitados quando o quadro demora. As escritas de velocidade angular no corpo visual deixam de ocorrer a cada quadro: o giro é atribuído no impacto e integrado pelo Unity. Quando o giro fica insignificante ou a bola é agarrada, o trabalho adicional é interrompido. Não foram reduzidas resolução, qualidade gráfica ou configuração do headset.

No cenário emulado de um segundo a 90 FPS com a bola girando, a revisão 2 fez 240 chamadas adicionais ao motor; o fluxo anterior corresponde a 630 chamadas no mesmo cenário. Redução de 61,9% nesse contador específico, não uma medida de redução total de CPU/GPU nem uma promessa de FPS. O executável do teste sem renderização conseguiu iniciar o Unity e carregar a arena. Os contadores de bola permaneceram em zero nesse modo: não havia bola ativa e não foram testados contatos reais.

Resultados: dez verificações da matemática compilada e nove cenários de emulação, incluindo limites de frequência, ausência de escritas repetidas de rotação e consistência de trajetória em 10, 30 e 90 FPS simulados. Os arquivos da primeira versão foram preservados em `versions/v1/` para comparação, não para instalação automática.

## Resultado

- Aparência adaptada à **Mikasa Beach Pro BV550C**. O nome do modelo foi confirmado na [apresentação oficial da Mikasa](https://mikasasports.com/mikasa-launches-new-beach-volleyball-at-pro-tour/) e a referência visual na [página oficial do produto](https://mikasasports.com/shop/beach-volleyball/bv550c/). A [Mikasa](https://mikasasports.co.jp/e/sports/bv550c-wybr/) descreve as cores amarelo, azul e vermelho.
- Atlas novo, produzido localmente a partir de desenho vetorial. Não é uma textura oficial extraída da fabricante. A geometria original de 18 painéis foi mantida: é uma adaptação visual, não uma reprodução exata da construção da BV550C. Mapas de relevo e oclusão originais preservados.
- Giro físico calculado a partir da velocidade da mão no ponto de contato, incluindo a estimativa de movimento angular do controlador fornecida pelo próprio jogo.
- Efeito Magnus experimental: a rotação influencia moderadamente a trajetória. Isso é separado do giro visual. A sincronização da velocidade angular com o corpo visual local também foi acrescentada.
- Física adicional habilitada apenas quando `PhotonNetwork.OfflineMode` retorna verdadeiro. Não atua em salas online, incluindo salas privadas online. A aparência é aplicada em todos os modos.

## O que foi encontrado no código

`Volleyball.SetRandomAngularVelocity` (RVA `0x77F430`) atribui rotação aleatória ao corpo rígido. `Client_ChangeMotion` chama essa rotina em determinados toques, mas pula essa chamada quando o identificador de quem tocou corresponde ao jogador local. Portanto, não bastaria substituir apenas a rotação aleatória.

O mod coleta os dados do contato ao entrar em `PhysicalBody.HandleVolleyballCollision` (RVA `0xEEB3B0`) e aplica o giro somente no ponto em que o fluxo original aceitou a batida e chamou `InvokeRpc_ChangeMotion` (chamada em `0xEED250`). A validação original do toque, resposta normal, pontuação e propriedade de rede continuam sendo executadas.

O método original `PhysicalBodyPart.GetVelocityAtPoint` inclui as estimativas de velocidade linear e angular da parte do corpo. Os campos e offsets foram conferidos nos metadados IL2CPP, não inferidos apenas pelos nomes.

## Modelo físico experimental

Para vetor `r` do centro da bola ao contato, velocidade da mão `vh`, velocidade da bola `v` e rotação atual `w`:

`w_nova = limitar(w + 0,60 * (r × (vh - v - w × r)) / |r|², 60 rad/s)`

O produto vetorial descarta a componente normal. O fator 0,60 vem de uma aproximação de esfera oca e contato tangencial aderente com uma mão de massa efetiva elevada. Não é uma calibração experimental deste jogo nem um modelo completo de atrito: não há limite de impulso tangencial por Coulomb nem estimação da deformação da bola.

`a_Magnus = limitar(0,005 * (w × v), 8 m/s²)`

A aceleração é integrada na atualização local da bola até 30 vezes por segundo, com tempo acumulado e integração pelo ponto médio em passos internos limitados. Intervalos inválidos ou superiores a 0,25 s são ignorados para evitar saltos grandes. O coeficiente é uma escolha inicial ajustável, não uma medição aerodinâmica da BV550C. O amortecimento angular original continua valendo. A física adicional é desligada quando a bola é agarrada ou o modo deixa de ser offline; a verificação de modo ocorre no próximo passo adicional, antes de aplicar força.

## Arquivos e reversão

Somente dois arquivos da instalação são substituídos:

1. `GameAssembly.dll`: quatro pontos de ligação e novas seções de código, constantes, estado e metadados de execução. Código não fica gravável; dados não ficam executáveis. Relocações ASLR e informações de desenrolamento da pilha foram acrescentadas. Não usa carregador de mods, DLL externa ou chamadas de rede.
2. `VolleyballFever_Data\resources.assets`: somente o objeto de textura `VolleyballD`, PathID 40, é alterado. Os outros 1.299 objetos serializados permanecem idênticos byte a byte. A textura BC7 foi reaberta e decodificada após salvar. Os níveis de mipmap passam de 11 para 9, até 4×4, conforme o codificador utilizado.

Os originais ficam em `backup/`; `working/` contém a cópia completa modificada. Nenhum arquivo de `sources/` foi alterado. Nenhum arquivo do jogo foi enviado a serviços externos.

Com o jogo fechado, o script `Install-or-Restore.ps1` oferece:

- `-Mode Full`: aparência e física experimental.
- `-Mode SkinOnly`: apenas aparência, restaurando a lógica original.
- `-Mode Restore`: restaura os dois originais.

O script confere os hashes antes de instalar e interrompe se encontrar outra versão ou outra modificação. Uma atualização do Steam exige nova análise. A verificação de integridade pela Steam também pode restaurar os arquivos oficiais.

Para facilitar, com o jogo fechado, dê dois cliques em `Restaurar-original.cmd`, `Somente-aparencia.cmd` ou `Ativar-mod-completo.cmd`. Esses atalhos chamam o mesmo script e mantêm a conferência dos arquivos.

## Verificações concluídas

- Dez verificações do código C compilado: direção do giro, simetria de raspadas opostas, contato normal sem giro artificial, limite de rotação, redução de escorregamento, sentido e limite do Magnus e entrada degenerada.
- Nove cenários do código de máquina final em emulador de CPU com funções do motor simuladas: raspada local aceita, sentido contrário, toque normal, modo online sem aplicar física adicional, toque rejeitado, imagem realocada por ASLR, frequência de 30 Hz e comparação de trajetórias a 30 e 10 FPS com a referência de 90 FPS.
- Conferência dos endereços, instruções substituídas, saltos de retorno, permissões de seções, relocações e tabela de exceções do arquivo final.
- Textura serializada reaberta; todos os objetos não visados comparados byte a byte.
- Prévia local da textura sobre a malha extraída em `assets/Mikasa-mesh-preview.png`. Não é captura do jogo.

**A inicialização sem renderização foi verificada; ainda não houve teste de renderização ou jogabilidade com headset.** Os testes de emulação usam funções simuladas e não comprovam a integração da física com o motor real, a disponibilidade dos dados de contato em execução, a sensação física ou a compatibilidade dos preditores de trajetória da IA com Magnus. Este pacote é um protótipo para teste offline, não um mod validado em partida.

## Teste mínimo no headset

1. Abra o jogo pela Steam e confirme que a bola mostra a aparência nova.
2. Entre no modo local/offline do jogo; uma sala privada online não habilita este mod de física.
3. Compare uma batida frontal com raspadas laterais opostas, tentando manter a força semelhante. As raspadas devem produzir sentidos de giro opostos; a batida frontal não deve adicionar giro tangencial artificial.
4. Faça uma raspada por cima e outra por baixo. Observe separadamente a rotação da marca na bola e uma eventual mudança de trajetória.
5. Se o jogo não abrir ou a física se comportar mal, feche-o e use `SkinOnly` para continuar com a aparência, ou `Restore` para voltar integralmente ao original.

O ajuste seguinte depende dessa observação: transferência insuficiente, giro excessivo e curvatura excessiva são controles diferentes.

## Fontes das ferramentas

Análise estática local com [Il2CppDumper 6.7.46](https://github.com/Perfare/Il2CppDumper/releases/tag/v6.7.46), [UnityPy](https://github.com/K0lb3/UnityPy), Capstone e pefile. Compilação local com [Zig 0.14.1](https://ziglang.org/download/). Testes de código com [Unicorn](https://www.unicorn-engine.org/). Fontes do mod e scripts de reprodução ficam nesta pasta. Nenhum bypass de DRM ou anticheat foi implementado.
