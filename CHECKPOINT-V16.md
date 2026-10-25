# Cloudcourt VR v16 — 24/10/2026

Base: v15-rostos. Backup completo verificado em versions/v15-rostos-antes-puloviva.

Identidade: Cloudcourt VR. Design de menu principal, pausa, skins e placar criado em camadas editáveis no Figma: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24 . Paleta azul, coral, creme, amarelo e marinho. Fonte Baloo 2 ExtraBold sob OFL.

Implementado: quadra com metades azul/vermelha, postes e fita com novo nome, faixas decorativas e dois placares de parede no indoor, antenas sem colisão, luvas cartoon abertas/fechadas, cabelo cobrindo a nuca do personagem de cabelo longo, menus e popup de ponto menores. Tela de boas-vindas e botões do Discord removidos. Referências técnicas do executável e Steam permanecem para compatibilidade.

Jogabilidade: limite de movimentação simétrico pela posição do torso (inclui deslocamento físico do headset), redes das cenas alinhadas ao plano central, levantamento dos bots 4v4 e assistência do segundo toque para janela lateral a 1,15 m da rede, assistência no primeiro toque de cada posse em 2v2/4v4, salto dos bots +70 cm sobre o original (+30 cm sobre v15), margem vertical no ataque de terceiro toque. Física online e saque na mão preservados.

Online: Blue Team/Red Team, quatro skins escolhidas no menu e retransmitidas para jogadores que chegam depois; troca por vaga ocupada por bot, aplicada entre pontos se solicitada no rally. High five reconhece a posição física das mãos e a passagem entre quadros, funciona no lobby e durante a partida. A complementa trigger nos menus Oculus/OpenVR.

Validação: leitura de malhas e referências, código nativo em duas bases de memória, regressões de modos/saque/física, testes de nova assistência, ataque, high five, skins, troca de formação e entrada A/trigger. Executável inicializado no menu/indoor e na praia. Instalador verifica hashes, atualização da v15-rostos, repetição, restauração e rejeição de arquivos danificados.

Limite: ainda não houve playtest desta versão no Quest 3 nem sessão real entre dois PCs. A prévia do Figma não é captura do jogo. A implementação Unity segue a identidade e os controles do design, com adaptação à interface existente. A troca por outro humano num time cheio não é automática; o outro time precisa de vaga de bot.

Pacote: Cloudcourt-v16-checkpoint.zip. Sala v16 fica separada da v15. Para voltar: Restaurar.cmd e depois instalar Caioba-completo-v15-rostos.zip.

Retomada: identity_v16.c, build_cloudcourt_v16.py, create_puloviva_characters.py (nome técnico herdado), create_cloudcourt_font.py, package_cloudcourt_v16.py; arte em assets/cloudcourt-v16. Não executar geradores antigos por cima dos arquivos novos.
