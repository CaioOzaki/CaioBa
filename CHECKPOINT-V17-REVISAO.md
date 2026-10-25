# Cloudcourt VR v17 - revisao das alteracoes v16

Base: Cloudcourt-v16-menu-corrigido. Backup verificado dos dez arquivos e das fontes em versions/cloudcourt-v16-antes-revisao. Os ZIPs anteriores foram preservados.

## Falhas confirmadas e corrigidas

1. Maos: o mesmo modelo assimetrico era usado na esquerda e na direita, com polegar no lado oposto ao esqueleto. Agora sao quatro malhas distintas: esquerda/direita, abertas/fechadas. O espelhamento inclui normais e ordem dos triangulos. Rastreamento, raizes, colisores e materiais permanecem intactos.
2. Pausa solo: o estimador de velocidade continuava executando com deltaTime zero durante a pausa. Mesmo uma mao parada gerava NaN, que permanecia nas amostras apos Resume e chegava a Hand.GetVelocity. Dois pontos especificos agora usam tempo real de rastreamento. A simulacao do jogo continua pausando normalmente. O teste reproduz o defeito anterior e exercita tambem a DLL final. A contaminacao de bola/previsao/IK explica o caminho provavel para os bots sumirem; a confirmacao completa em headset ainda depende de playtest.
3. Dados de bola invalidos: os hooks de movimento local e recebido agora recusam posicao ou velocidade NaN/Inf antes de propagar o quadro para fisica/rede. Quadros validos, inclusive bola parada, continuam passando.
4. Placares na parede: os quatro textos herdaram estado inativo, impedindo renderizacao e GameObject.Find. Foram ativados com a fonte Cloudcourt, grupos opacos e raycast decorativo desligado.
5. Skins e times: uma atualizacao de aparencia atrasada podia restaurar o campo do time antigo sem mover o jogador entre as listas. Skins agora preservam a filiacao existente; somente um pedido explicito de troca move o jogador.
6. Cache online: as atualizacoes de aparencia a cada tres segundos usavam RPC armazenado, acumulando 1.200 eventos por jogador/hora. O envio agora e confiavel e ordenado, sem armazenar historico desses eventos.

## Revisao de outros sistemas

Rede visual e volumes principais centralizados em Z=0 nas cenas examinadas; antenas continuam sem colisores. Assinaturas nativas de placar, popup, audio e high five conferidas. O codigo original restaura a pose das maos a cada quadro, antes do feedback de levantamento. Nao foi aplicada uma suposta correcao de eventos Resume/Leave: as entradas persistentes suspeitas tinham alvo nulo e eram inertes; o caminho nativo de pausa/retomada e valido.

Nao foram encontrados nomes antigos nos textos UI/TMP examinados. Cabelo preto, roupa vinho, novo logo de carregamento, correcoes anteriores do menu e raycast, assistencias e demais funcionalidades foram preservados.

## Validacao e limites

Passaram 15 suites independentes de regressao, mais a suite de funcionalidades v16 e 20 casos focados em skin/time/RPC. As suites incluem fisica, 2v2/4v4, saque, recepcao, formacao, salto, high five, dados de movimento, menu, maos e placares. O teste de pausa executa o codigo x64 original e corrigido com APIs Unity controladas, incluindo ShowMenu, frames pausados, Resume e leitura da velocidade, em duas bases de memoria. Testes de assets preservam objetos nao relacionados.

Ainda nao houve teste fisico desta revisao no Quest 3 nem partida real entre dois PCs. O gesto de maos abertas e aplicado localmente; a pose vista por outro cliente segue o mecanismo de pose original. Esses testes automatizados nao comprovam toda a experiencia visual ou de rede em VR.

## Distribuicao

Pacote: Cloudcourt-v17-revisao.zip. Instalador completo com dez arquivos, validacao de hashes, backup e restauracao. Aceita o original Steam build 9216628 ou Cloudcourt-v16-menu-corrigido. Restaurar.cmd volta os dez arquivos ao original compativel.

As salas usam Cloudcourt-2v2-v17 e Cloudcourt-4v4-v17 para evitar misturar a revisao com clientes antigos. Todos os amigos devem instalar a v17 e escolher a mesma regiao e modo. O GitHub deve continuar sem os arquivos exclusivos das tentativas Volley Riot; nao publicar DLLs, assets extraidos, backups ou ZIPs do jogo.

Fontes da revisao: fix_gloves_v16.py, fix_wall_boards_v17.py, fix_pause_v16.py, identity_v16.c, spin_mod.c, online_2v2.c, build_patch.py e build_cloudcourt_v16.py; testes correspondentes; package_cloudcourt_v17.py. Relatorios locais em analysis/v17-regressions.json, v16-pause-regression.json, v16-identity-rpc-tests.json, v17-motion-finite-tests.json, v16-glove-validation.json e v17-wall-board-validation.json.
