# Cloudcourt VR v19 — Customizacao, bots e mapas online

Release: **Cloudcourt-v19-customizacao**, 25/10/2026.
Base: Cloudcourt-v18-praia-lobby, commit 9d636710ffe0a6cb1bac13050b22cd981f78fd9f.
Backup preservado: `versions/cloudcourt-v18-antes-v19`, 17 arquivos e fontes.
ZIP anterior preservado: `distribution/Cloudcourt-v18-praia-lobby.zip`.
`sources/` permanece somente leitura; nenhuma alteracao nos arquivos sincronizados.

## Mudancas implementadas

- Corrigido o caminho real de salto dos bots: Bot.Update fazia Jump internamente
  e ignorava o antigo hook. O apice real passa de 1m para 2m. No terceiro toque,
  o atacante aguarda a bola parar de subir e inicia o salto na janela de descida.
  Decisoes apenas no dono Photon do bot, para solo/online e 2v2/4v4.
  O alvo e arco do levantamento aprovado pelo usuario permanecem identicos a v18.
- Nove faces independentes: Cool (oculos escuros), Nerd, Smirk, Goofy, Crying,
  Surprised, Gigachad, Glam (cilios/batom) e Pleading. Os quatro desenhos antigos
  do Cloudcourt foram preservados; os cinco novos sao arte propria.
- Nove roupas: regatas preta/branca; ternos preto/branco; camisetas branca,
  preta, azul, verde escura e vinho. Total 81 combinacoes de face e roupa.
- Painel CUSTOMIZE no menu principal e na pausa, com previews e botoes de
  anterior/proximo. Preferencias persistentes; cada jogador sincroniza sua
  escolha online. Abrir/fechar o painel nao recria a partida nem os bots.
- A preservado e gatilhos digitais/analogicos das duas maos adicionados ao
  mesmo estado de clique. Laser segue na mao direita; qualquer gatilho clica
  no botao sob esse laser. Histerese analogica 0,60/0,35 evita cliques oscilantes.
- Cliques validos de botao tocam feedback 2D original de 80ms, com fonte e clipe
  em cache. Trigger sobre UI no lobby nao solicita uma bola de treino.
- Fontes de mar/passaros da praia silenciadas; demais sons mantidos.
- Selecao de mapa online antes de CREATE ROOM: Indoor ou Beach. A propriedade
  Photon Cloudcourt.Map definida pelo host comanda o mapa de todos os clientes.
  Sala 2v2 comporta 4 jogadores; 4v4 comporta 8. Propriedade ausente/invalida usa
  Indoor; NightScene legado e convertido para Beach dia.
- Nome Beach e praia noturna retirada da selecao. O arquivo legado permanece
  instalado para integridade/restauracao e conversao de referencias antigas.
- Opcoes de sets/pontos retiradas. Melhor de tres sets (duas vitorias), todos
  os sets Indoor 25/Beach 21, preservando a vantagem de dois pontos.

## Instalacao e amigos

Extraia todo o ZIP e execute Instalar.cmd com o jogo fechado. Compatibilidade:
original Steam build 9216628 ou a v18 anterior. Abra pela Steam depois.
Restaurar.cmd retorna os 17 arquivos ao original compativel. O instalador
verifica todos os hashes antes de alterar arquivos e gera backup recuperavel.
Nao force encerramento de uma partida para instalar.

Todos os amigos devem instalar v19, mesma regiao e formato. Namespaces:
`Cloudcourt-2v2-v19` / `Cloudcourt-4v4-v19`.
Previews PNG: `assets/customization-v19/preview-faces.png` e
`assets/customization-v19/preview-outfits.png`.

## Verificacao e limites

23 suites nativas passaram em `analysis/v19-regressions.json`: fisica, formacao,
saques, rede/online, recepcao, levantamento, hooks, high five, dados finitos,
pausa, luvas, placares, RPC, lobby, gameplay real, combinacoes de customizacao,
input e escolha de mapa. Testes novos incluem fluxo original Bot.Update e
EndRally/EndSet em 16 combinacoes, 324 casos nativos de aparencia e retorno float
XMM0 do invocador de interface real. O teste geometrico complementar encontrou
contato com bola a 3,744m; isso nao equivale a uma partida VR real.

Tres suites de assets finais passaram, com comparacao ao backup v18:
menu 108 pontos de clique e modal; atlas 81 combinacoes e UVs; silencio da praia.
`analysis/v19-final-assets-tests.json` confirma que apenas os objetos previstos
mudaram. Geometria, indices, normais, limites e colisores dos avatares mantidos;
dois atlas BC7/mipmaps somam 6.291.488 bytes, sem novos draw calls do avatar.

Testes automatizados e inicializacao controlada sem VR nao confirmam sensacao,
interacao fisica no Quest 3 nem comportamento em partida real entre dois PCs.
Esses playtests continuam pendentes, incluindo pausas, high five, escolhas de
mapa/skin, bolas de lobby, ataque dos bots e input do menu.

## Recuperacao e publicacao

`installation-status.json` e `analysis/github-publication.json` locais registram
o ZIP/hash, backup da instalacao e commit efetivamente publicados. O checkpoint
de fontes apos entrega fica em `versions/cloudcourt-v19-fontes`.
Publicar somente fontes, arte propria e materiais com licenca verificavel.
DLLs, assets originais, backups e ZIP de distribuicao ficam locais. Preservar
a limpeza da branch sem reintroduzir experimentos abandonados.

A automacao Retomar Cloudcourt do checkpoint continua ativa entre entregas;
sem nova tarefa pendente, nao modificar o projeto nem repetir avisos de testes.
