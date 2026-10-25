# Cloudcourt VR — game design v16

Vôlei VR social e cartoon para Quest via PCVR. A personalidade é acolhedora, expressiva e esportiva: corpos redondos, luvas macias, ternos divertidos e emojis. O nome escolhido é Cloudcourt VR; a escolha criativa não equivale a registro de marca.

## Experiência

Receber com confiança, levantar com intenção, correr para atacar e comemorar com amigos. A física preserva o controle da direção e do efeito da bola. A assistência reduz frustração sem decidir todos os contatos.

Os pilares são rallies cooperativos de três toques, leitura imediata dos times, conforto em VR e identidade cartoon consistente. Não acrescentar obstáculos físicos decorativos nem efeitos que encubram a bola.

## Modos e regras

Solo e online com 2v2 e 4v4. Indoor e praia de dia permanecem os ambientes principais. Azul ocupa o lado negativo de Z e vermelho o positivo. A rede visual, a colisão e os limites de movimento compartilham Z=0.

No 4v4, formação em cruz: fundo cobre a recepção, jogador da rede prepara, pontas atacam. A recepção procura o levantador; o segundo contato oferece uma janela de ataque próxima à rede, em vez de seguir a posição atual do atacante. Bots aliados evitam bloqueios e priorizam três contatos. O ataque recebe altura e trajetória suficientes para a rede elevada.

A ajuda de recepção vale para o primeiro toque do time a cada posse, incluindo a recepção do saque. No segundo toque, segurar os dois GRABs ativa levantamento para uma janela a aproximadamente 1,15 m da rede, com alvo lateral previsível. Soltar um GRAB permite ataque de segunda. Luvas abertas comunicam o modo de levantamento.

Saque humano nasce na mão pelo trigger. Saque de bot nasce sobre o sacador. Mantidas as faltas implementadas de saque dentro da quadra e bloqueio de saque.

## Direção visual e interface

Paleta: azul vivo, coral vermelho, creme, amarelo de destaque e azul-marinho profundo. Quadra dividida em duas cores com linhas claras; zonas de ataque visíveis. Ginásio com painéis geométricos, faixas de torcida e dois placares de parede grandes, legíveis dos lados opostos. Antenas listradas são apenas decorativas.

Menus usam cartões arredondados, títulos curtos e tipografia Baloo 2 de formas arredondadas, sob licença OFL. Placar: azul à esquerda, vermelho à direita, números grandes e poucos detalhes. O aviso de ponto é compacto: cor, +1 e motivo abaixo. A tela de boas-vindas e os convites ao Discord são removidos.

No online, os times são nomeados pelas cores. O menu de pausa inclui troca de time e quatro escolhas de terno/emoji. Uma troca respeita a capacidade e atualiza tanto a formação quanto o avatar, ocupando a vaga de um bot. Durante o rally, a solicitação é aplicada ao final do ponto para preservar o saque e a jogada. O botão A complementa o trigger nos menus.

## Interação social

High five disponível no lobby e durante toda a partida online. Contato detectado por proximidade e movimento relativo, incluindo mãos que cruzam entre quadros. Resposta curta de aproximação visual e som de palma; exige afastamento para repetir. Sem travar permanentemente a mão ou mover a câmera do jogador.

## Limites e validação

O projeto continua sendo um mod que depende de uma instalação compatível do jogo base. A identidade visual nova não transforma os sistemas herdados em um executável independente. Não alterar identificadores técnicos necessários para Steam ou Photon ao substituir marcas visíveis.

Antes da entrega: conferir simetria da rede, trajetórias em ambos os lados, recepção por posse, opções online, escolha de skins entre dois clientes, gesto de levantamento, menus com A e saque/ataque dos bots. Testes automatizados não substituem partida real no Quest. Priorizar poucos materiais, malhas leves e ausência de alocações por quadro. Salvar checkpoints com ZIP, backup e fontes no GitHub.

Design editável: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24
