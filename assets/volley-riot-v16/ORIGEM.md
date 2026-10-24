# Arte Volley Riot v16

Logo, quadra, fita da rede, proteção dos postes e tecido das luvas foram criados para este mod com a ferramenta ImageGen. As imagens finais estão nesta pasta e são incorporadas aos assets pelo builder.

A fonte **Lilita One**, de Juan Montoreano, foi obtida do repositório oficial Google Fonts e é distribuída sob SIL Open Font License. A licença acompanha a fonte. `cartoon_font_v16.py` gera a representação SDF usada pelo TextMeshPro.

As luvas são malhas novas construídas em `make_hands_v16.py`; somente as matrizes de ligação do esqueleto local são aproveitadas para compatibilidade com a animação. `repair_hair_v16.py` acrescenta volume posterior ao personagem de cabelo comprido produzido no checkpoint v15. Nenhuma malha extraída do jogo é armazenada nesta pasta.

Paleta: creme `#FFF5DC`, marinho `#10233F`, azul `#2468DF` e vermelho `#E74750`.

Prompt do tecido: albedo quadrado, quatro quadrantes iguais nas cores da paleta, trama fina de tecido esportivo de baixo contraste, iluminação uniforme, sem texto, objetos ou perspectiva. A imagem é amostrada pelas UVs da geometria das luvas.
