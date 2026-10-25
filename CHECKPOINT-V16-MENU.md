# Cloudcourt VR v16 - menu corrigido

Base: Cloudcourt-v16-cabelo-preto. Backup completo dos dez arquivos em versions/cloudcourt-v16-antes-menu-fix.

Problema reproduzido nos assets: os dois titulos adicionados ao menu herdaram ancoras esticadas do texto de um botao. Suas areas efetivas eram 1500 x 448, sobrepondo todos os botoes e aceitando raycasts. O laser atingia esses textos sem encontrar um Button ancestral. Por isso trigger e A nao acionavam os botoes, embora o encaminhamento nativo dos controles funcionasse.

Correcao: ancoras centrais, areas de titulo 700 x 48, textos e RawImages decorativos sem raycast; as imagens dos botoes continuam recebendo raycast. Desativados o Splash antigo da pagina Start, a pagina Intro e a pagina DailyChallenge residual. Os listeners UnityEvent e os modulos de entrada permanecem byte a byte iguais.

A textura Logo de globalgamemanagers.assets foi substituida por arte original Cloudcourt VR, mantendo dimensoes e formato DXT5. A mesma textura e usada por PlayerSettings.m_VirtualRealitySplashScreen e pelos RawImages do menu. Isso corrige a tela de carregamento do headset, alem do logo no menu. Apenas o objeto Texture2D 3 mudou nesse arquivo; scripts e referencias permaneceram intactos.

Validacao: teste de hit-test em 36 pontos nos quatro botoes; os 36 eram interceptados na versao anterior e agora chegam ao botao esperado. Conferencia dos anchors, eventos, flags, logo e demais objetos globais. Testes nativos v16, incluindo A e trigger, aprovados em duas bases de memoria. O teste de raycast usa coordenadas do canvas; ainda e necessario confirmar no Quest 3 o rastreamento, foco e clique reais.

Distribuicao: Cloudcourt-v16-menu-corrigido.zip, com dez arquivos modificaveis. Instalacao sobre original Steam build 9216628 ou Cloudcourt-v16-cabelo-preto. Instalador verificado numa copia separada para instalacao, upgrade, repeticao, restauracao e recusa de arquivos danificados. Restaurar.cmd retorna os dez arquivos ao original compativel. Os ZIPs anteriores foram preservados.

O protocolo online e o codigo nativo permanecem iguais a v16. Cabelo preto, roupa vinho, fisica, modos e identidade Cloudcourt preservados. O repositorio continua limpo dos arquivos exclusivos das tentativas Volley Riot.

Fontes principais desta correcao: fix_cloudcourt_menu_v16.py, test_menu_raycast_v16.py, build_cloudcourt_v16.py, Apply-Complete-Mod.ps1 e package_cloudcourt_menu_v16.py. A correcao tambem e aplicada pelo builder completo para evitar regressao em futuros rebuilds.
