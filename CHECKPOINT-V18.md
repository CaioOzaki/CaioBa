# Cloudcourt VR v18 — praia, sons, levantamento e lobby

Base: Cloudcourt-v17-revisao. Backup recuperavel dos 17 arquivos afetados e
fontes anteriores em versions/cloudcourt-v17-antes-v18. ZIPs anteriores mantidos.
Novo pacote: Cloudcourt-v18-praia-lobby.zip. sources/ permanece somente leitura.

## Sons

Os 22 AudioClips inventariados foram substituidos. Impactos e clique de menu
usam Kenney Impact Sounds e Interface Sounds, sob CC0, com licencas originais
e creditos incluidos. Musica, vinhetas de ponto, alertas, ondas e passaros
foram sintetizados do zero por build_audio_v18.py. Nenhum som do jogo original
foi amostrado. As vozes de ponto deram lugar a vinhetas distintas dos times;
o placar informa azul/vermelho. Nao foi necessaria gravacao de voz.

Bancos FSB5 PCM16 mono a 22050Hz; ambientes/musica usam streaming. Cada banco
foi decodificado por FMOD e comparado amostra por amostra com o WAV novo,
inclusive apos serializacao. Picos normalizados e transicoes contra estalos.
Fontes oficiais verificadas em 25/10/2026: https://kenney.nl/assets/impact-sounds
e https://kenney.nl/assets/interface-sounds.

## Praia

Sunbeam Cove: coqueiro proprio com tronco curvado, folhas largas facetadas e
cocos simples. 261 vertices e 512 triangulos (antes 831); 17 instancias por
cena compartilham mesh/material. Atlas opaco e areia/normal de 512px com
mipmaps; sem folhas transparentes nem animadores sem controlador. Terreno em
enseada crescente com dunas suaves; quadra e area de corrida planas. Piramides
de erro/altura do Terrain recalculadas. Shaders e colisores preservados.
Aplicado nas cenas praia dia/noite usadas por solo e online.
Preview: assets/beach-v18/preview-palm.png (geometria gerada, nao captura VR).

## Levantamento

Dois GRABs no segundo toque: escolhe atacante elegivel do mesmo time e projeta
sua coordenada lateral para a faixa a 1,15m da rede, evitando pontas fixas.
Em quarteto prefere as pontas e informa o receptor a selecao tatica dos bots.
Mantem chegada a 2,65m e arco elevado; alvos dentro das linhas. Caminho local
e online de 2v2/4v4; soltar um GRAB desativa a assistencia.

## Lobby online

Antes da partida, movimento pelos dois lados limitado a x +/-10m, z +/-15m.
Um trigger de qualquer mao cria uma bola na propria mao; Hand.Update original
segura, solta e arremessa. Cada bola e um objeto Photon pertencente ao cliente
que a criou. Ate quatro bolas por cliente: pedidos seguintes reciclam soltas.
Intervalo minimo de 0,25s; maos remotas nao leem o trigger local.

Bolas de treino nao alteram a contagem de toques nem a singleton da bola
oficial. Antes de TransitionIntoGame, sao desativadas, soltas de eventuais
maos e destruidas pelo proprietario. Entrada na partida restaura o caminho
original de movimento/saque/pontuacao. Host e clientes usam o mesmo fluxo.
Cada bola de treino tem sua propria cadencia de spin/Magnus, sem depender
apenas da bola tocada mais recentemente.
Bolas Photon recebidas do cache antes de ativar a pagina da sala sao
registradas no primeiro LateUpdate do lobby e entram na mesma limpeza/fisica.

## Verificacoes e limites

Passaram 20 suites: fisica, 2v2, formacao, espera/regras de saque, online,
recepcao, levantamento, hooks, salto/high five, dados finitos, pausa, menu,
luvas, placares, funcionalidades, RPC de skin/time, novos alvos, lobby e assets.
Levantamento: 96 casos em ambos times/formatos/caminhos e duas bases de memoria.
Lobby: codigo x64 compilado e Hand.Update original com Unity/Photon controlados.
Assets reabertos para conferir indices, referencias, shaders e colisores.
Praia dia e noite: processos de inicializacao ativos durante 15s cada.

Nao houve teste fisico no Quest 3 nem partida real entre dois PCs. Conferir
percepcao visual/sonora, abertura da praia em VR, atacantes em movimento e
treino compartilhado no lobby. As verificacoes nao comprovam toda a experiencia.

Instalador reversivel de 17 arquivos com hashes, backup e restauracao; aceita
original Steam build 9216628 ou v17-revisao. Outras versoes devem restaurar o
original antes. Todos os amigos precisam da v18 e mesma regiao/modo.
Salas: Cloudcourt-2v2-v18 / Cloudcourt-4v4-v18.

Publicar fontes, arte propria e os tres efeitos CC0 com licencas. Nao publicar
DLLs, assets extraidos, .resource, backups ou ZIPs no GitHub. Preservar a limpeza
da branch e nao reconstruir visual v16 sobre assets v18.
