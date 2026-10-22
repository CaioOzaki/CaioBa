# Caioba — fontes do mod

Registro do projeto pessoal de modificacoes para Volleyball Fever, Steam build 9216628. Este repositorio nao inclui o jogo original nem constitui um jogo independente.

## Estado preservado

- Codigo de gameplay v10: modos 2v2/4v4, selecao online, movimentacao, assistencia na recepcao, bots e regras de saque.
- Indoor Caioba e postes quadrados corrigidos.
- Praia v12: novo terreno de dia e noite, dunas e costa curva.
- Instalador completo v12, restauracao, empacotamento e testes.
- Desenhos Caioba em SVG, criados para o mod.

## Arquivos principais

`spin_mod.c` inclui os modulos `mode_2v2.c`, `formation_serve.c` e `online_2v2.c`. `build_patch.py` aplica o codigo nativo compilado em uma copia local do jogo. Os scripts `test_*.py` verificam comportamentos especificos.

`build_caioba_maps.py` corresponde ao indoor e ajustes v11. **Nao executa a praia v12**: essa etapa esta em `build_beach_v12.py`. Nao reinstale mapas antigos por engano. Consulte `MAPAS-CAIOBA.md` para o historico.

`package_complete_mod.py` gera o ZIP completo v12, confere os arquivos contra a instalacao local e testa o instalador em uma copia isolada. `Apply-Complete-Mod.ps1` e o instalador atual. Os outros instaladores e empacotadores foram mantidos como historico e nao devem ser usados como substitutos do pacote atual.

## Dependencias locais

Os scripts foram feitos para o ambiente Windows atual e alguns ainda usam caminhos locais. Eles dependem de uma instalacao propria compativel, copias em `working/`, originais em `backup/` e bases de mapas em `versions/`, alem das ferramentas de compilacao e bibliotecas Python. Esses arquivos nao sao enviados ao GitHub. Nao existe ainda uma compilacao automatica do projeto a partir de um clone vazio.

Os PNGs, o gerador da arte Mikasa, a textura Mikasa, arquivos extraidos do jogo, executaveis, bibliotecas de terceiros, backups, logs e ZIPs foram excluidos deste repositorio. Os scripts que usam esses insumos exigem que estejam presentes localmente. O ZIP de distribuicao permanece guardado separadamente no computador.

## Validacao conhecida

O pacote v12 passou pelos testes de instalacao, instalacao repetida, restauracao, atualizacao do pacote antigo de codigo e rejeicao de arquivos incompatíveis ou corrompidos. As cenas de praia dia/noite abriram no executavel em testes de inicializacao. Ainda falta validar uma partida VR completa nos mapas novos e uma sessao online real entre dois PCs.

Este primeiro commit registra o estado atual. Versoes anteriores existentes apenas nos backups locais nao foram convertidas em historico Git.
