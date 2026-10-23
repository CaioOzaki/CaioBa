# Mapas Caioba v11

Instalados: indoor novo com cobertura entre 14 e 16 m (vigas a 13,72 m), quadra 9 x 18 m com linhas de ataque, arquibancadas laterais; praia dia e noite com terreno novo, dunas, passarela, abrigos e coqueiros reposicionados. Rede e postes Caioba. Atlas Mikasa BV550C reaplicado.

A DLL de jogabilidade v10 permanece instalada. Este pacote muda seis arquivos de cenas e materiais. O ZIP online v10 distribuido anteriormente NAO inclui estes mapas. Para jogar online com esta geometria, todos devem receber os mesmos mapas; a validacao de rede entre PCs continua pendente.

Validacao: leitura dos seis arquivos apos serializacao, indices das malhas, referencias locais, contato vertical no centro/recepcao/saque, decodificacao das texturas e alfa transparente da rede. Previa local renderizada a partir das malhas exportadas; nao representa a iluminacao final nem uma captura no headset. Sem teste em VR realizado nesta etapa.

Backup anterior completo dos arquivos tocados: versions/v10-antes-mapas. Para voltar SOMENTE aos mapas anteriores, feche o jogo e execute no PowerShell:

    & .\Install-Caioba-Maps.ps1 -Restore

Para reaplicar:

    & .\Install-Caioba-Maps.ps1

As fontes dos desenhos vetoriais e as previas ficam em assets/caioba. Os arquivos de jogo novos estao em maps-v11. A criacao e repetivel por build_caioba_maps.py a partir do backup anterior.


## Correcao apos teste em VR

O log Player-prev confirmou crash ao entrar em Scene (praia). A causa exata do crash nativo nao foi isolada. A praia foi reconstruida usando a estrutura original de cenas, terreno, colliders, scripts e shaders; apenas os coqueiros foram redistribuidos com ajuste de altura ao terreno. A enseada com passarela e abrigos da previa anterior foi retirada nesta revisao. A imagem praia-preview.png antiga nao representa esta revisao. O arquivo sharedassets1.assets foi restaurado byte por byte. Validada igualdade das tabelas de objetos e tipos e dos componentes de terreno/colisao/comportamento das duas praias. Ainda falta teste real de abertura em VR.

Piso indoor: invertida coordenada U; o renderizador de previas tambem foi corrigido para a convencao de coordenadas da Unity. Postes: substituido o empacotamento UV por faces inteiras com CAIOBA em letras verticais e retirados mapas antigos de relevo/oclusao. Backup desta revisao anterior em versions/v11-antes-correcao.


## Praia v12 — Enseada das Dunas

Nova topografia com costa curva, dois promontorios e dunas. Area da quadra e escape plana, coqueiros recolocados com alturas ajustadas ao terreno. Recalculados os limites e erros dos niveis de detalhe do terreno. Mantidos os shaders, tipos e componentes nativos, sem adicionar os objetos da primeira tentativa que crashava. Postes quadrados e indoor conferidos byte por byte e preservados.

Testes: abertura direta das cenas de dia e noite no executavel Unity em copia isolada, D3D11, 15 segundos cada, ambas sem crash. Nao houve partida VR completa nem teste da navegacao do menu para a praia. Logs em analysis/smoke-v12-day.log e smoke-v12-night.log.

Instalada por Install-Beach-V12.ps1. Para restaurar apenas a praia anterior: executar esse script com -Restore. Backup base em versions/v11-praia-estavel; hashes em maps-v12/manifest.json. build_beach_v12.py produz a nova praia; o antigo build_caioba_maps.py nao inclui v12. O ZIP online v10 nao inclui esta praia.
