# Cloudcourt v20.1 — Middle part do BOT1 restaurado

Release: Cloudcourt-v20-1-middle-part.
Base v20, commit 93a1825015f491a7fa5a3f853a8cc84c7d0d04a3.
Backup verificado: versions/cloudcourt-v20-antes-middlepart, 17 arquivos e fontes.
sources/ somente leitura. ZIPs entregues anteriormente preservados.

O bot asiatico BOT1 volta ao cabelo middle part anterior a v20. Geometria,
normais, UVs, indices e bone bounds conferidos exatamente contra o backup v19.
O corpo manteve seus 6194 vertices byte a byte; rosto, roupas e texturas nao mudam.
Os outros oito bots conservam suas melhorias de cabelo e nao foram alterados.

Delta no jogo: somente Mesh 4322 e AABBs dos renderers 3569/4235/4243 em
sharedassets0.assets. Todos os demais objetos desse arquivo permanecem iguais.
Os 16 outros arquivos da distribuicao, incluindo DLL, sao identicos a v20.
Nao houve recompilacao nem repeticao das 27 suites: seu binario e a logica sao
os mesmos previamente aprovados. A verificacao especifica desta restauracao
passou: analysis/v20-1-middlepart-tests.json, incluindo idempotencia.

ZIP completo: distribution/Cloudcourt-v20-1-middle-part.zip.
Extraia tudo e execute Instalar.cmd com jogo fechado. Aceita original Steam
build 9216628 ou v20. Restaurar.cmd retorna os 17 arquivos ao original compativel.
Namespaces permanecem Cloudcourt-2v2-v20 / Cloudcourt-4v4-v20; protocolo intacto.
O instalador confere hashes/backups e testa instalacao, upgrade e restauracao.
Teste novo no Quest nao foi realizado; a geometria visual coincide com a v19.

installation-status.json e analysis/github-publication.json registram ZIP,
backup de instalacao e commit efetivamente confirmados. github_commit null
significa publicacao ainda pendente. Fontes de entrega em versions/cloudcourt-v20-1-fontes.
Publicar somente fontes/arte propria; nunca binarios do jogo ou seus assets.
Manter automacao ativa e nao alterar o projeto sem tarefa autorizada.
