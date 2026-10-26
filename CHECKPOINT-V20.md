# Cloudcourt VR v20 — Personagens, customizacao e marcacao de pontos

Release: **Cloudcourt-v20-personagens-menu**.
Base: v19, commit 88f557fba16e5300c96af01f2600c0203fe8f886.
Backup verificado: `versions/cloudcourt-v19-antes-v20` (17 arquivos e 140 fontes).
ZIP v19 e fontes anteriores preservados. `sources/` continua somente leitura.

## Customizacao corrigida

A v19 carregava as duas texturas, mas o encoder BC7 gravava alpha quase zero,
sobretudo nos mipmaps. Testes antigos convertiam para RGB e perdiam o defeito.
A falha foi reproduzida no Unity sem VR e corrigida para BC3/DXT5 com alpha 255
em todos os niveis, mantendo os mesmos 6.291.488 bytes dos dois atlas.

Capturas reais Camera.Render/ReadPixels antes e depois:
`analysis/v20-customization-preview-before.png` e
`analysis/v20-customization-preview-after.png`.
O probe usa copia descartavel e restaura os PlayerPrefs. O menu/UVs/geometria
nao foram reconstruidos para essa correcao. O authoring agora usa BC3 explicito.

O cache de skin_body marcava o estilo como aplicado mesmo sem materiais prontos.
Agora retenta bindings atrasados/parciais e reaplica a materiais substituidos.
Teste x64 do codigo real reproduz a falha da v19 e comprova o novo comportamento.
Aplicacao no avatar vivo em Quest e dois clientes ainda requer teste pratico.

## Personagens e desempenho

Nove bots, com cabecas/cartoon e cabelos de cobertura continua e mechas curvas.
Os sete rostos anteriores foram mantidos, incluindo avo com cabelo preto e
roupa/tenis vinho. Novos:
- BOT8: menina branca, olhos escuros, cabelo preto longo com curtain bangs,
  mecha loira, septo, camiseta e calca pretas.
- BOT9: jovem branco alto/esguio, oculos pretos quadrados, cabelo medio-curto
  dividido ao meio/penteado para tras, camisa preta e jeans azul escuro.

O host seleciona identidades sem reposicao e envia o indice pelo RPC original.
Nao ha novo sorteio nos clientes. O conjunto e reiniciado no setup/clear da
partida; rodizio e troca de time nao trocam a identidade do bot.
Ate 8 slots podem usar 9 identidades sem repeticao, em solo/online e 2v2/4v4.

Os 48 atlas de variantes usam BC1/DXT1 opaco com 9 mips, reduzindo dados de textura
de 150.994.944 para 33.554.304 bytes. Rig, IK, animacoes e colisores preservados.
BOT9 tem geometria visual 10% mais alta/esguia; a fisica permanece igual.
Previews e arte propria em `assets/bots-v20/`.

## Placar, Settings, ginasio e bola

- Outline preta em HUD, popup de ponto e placares de parede, apos a atribuicao
  da fonte cartoon em runtime. Elementos decorativos nao bloqueiam o laser.
- Settings reorganizado em duas colunas, com slider, eventos, valores e fonte
  preservados. Opcoes de sets/pontos continuam ocultas.
- Faixas/suportes do ginasio afastados das vigas:12 intersecoes antigas viraram 0,
  com folga minima de 27,5 cm. Somente os vertices das faixas no Mesh 262 mudaram;
  estrutura, indices, outros canais de vertices e colisores mantidos.
- Ponto por queda no chao cria circulo verde dentro/vermelho fora no contato
  real, seguindo a decisao de limites das regras atuais. Contato e flags seguem
  no RPC EndRally confiavel existente, inclusive em erro de saque que caiu.
  Faltas sem contato no chao nao criam marca. O circulo e removido no proximo
  rally; tem 96 triangulos e nenhum colisor. Pontuacao e fisica nao mudam.

## Instalacao e amigos

ZIP: `distribution/Cloudcourt-v20-personagens-menu.zip`.
Extrair tudo e executar Instalar.cmd com jogo fechado; abre-se pela Steam.
Aceita original compativel Steam build 9216628 ou v19. Restaurar.cmd devolve
os 17 arquivos ao original compativel. Backup automatico antes de qualquer copia.
Todos os amigos precisam da v20, mesma regiao e formato:
`Cloudcourt-2v2-v20` / `Cloudcourt-4v4-v20`.

## Verificacao

27/27 suites passaram em `analysis/v20-regressions.json`. DLL SHA256:
718e924b207a3117472a08c7c5f663a708b4827cba4f2c1aee74f15316958c77.
Inclui 480 cenarios de bots,40 casos de marcacao, outline em duas bases ASLR e
regressao do cache de materiais. Testes originais de fisica/saque/formacao/
pausa/online/levantamento continuaram passando.

Auditoria final dos 6 assets: `analysis/v20-final-assets-audit.json`.
Reconstrucao byte a byte identica ao esperado, whitelist estrita e 450 mipmaps
opacos. Dez outros arquivos de dados identicos a v19; sem alterar fonts/rig/audio.
O pacote valida instalacao original, upgrade v19, repeticao/restauracao, backups
e rejeicao de arquivos, manifesto ou deltas invalidos.

O Unity desktop confirmou a correcao visual dos previews. Testes automatizados,
stubs e inicializacao controlada sem VR nao confirmam interacao no Quest 3,
aparencia aplicada ao avatar vivo ou partida real entre dois computadores.
Esses playtests continuam pendentes; nao fazer alteracoes especulativas por isso.

## Recuperacao e publicacao

`installation-status.json` registra instalacao/hash/backup efetivos;
`analysis/github-publication.json` registra o commit confirmado.
Se github_commit estiver null, a publicacao seletiva ainda deve ser concluida.
Apos entrega, fontes recuperaveis em `versions/cloudcourt-v20-fontes`.

Publicar somente fontes, testes, arte propria e materiais licenciados.
Nao publicar DLLs, assets originais, backups ou ZIPs. Preservar a limpeza da
branch sem reintroduzir experimentos abandonados. Manter a automacao ativa
entre entregas; nao modificar o projeto sem nova tarefa autorizada.
