# Checkpoint v15 — 23/10/2026

Implementado em 2v2 e 4v4, solo e online:
- Salto dos bots com ápice 40 cm maior, calculado pela velocidade vertical.
- Levantamentos 40 cm mais altos, também entre bots, incluindo a assistência com dois GRABs.
- Saque dos bots com impulso vertical maior: margem do arco aumentada em 65 cm para passar pela rede elevada.
- Bola do saque nasce 2,8 m acima da posição real do bot sacador. Ele aguarda embaixo dela durante a preparação.
- Sete modelos cartoon com cabeças maiores, corpos compactos e membros arredondados. Mantidas as identidades e animações existentes; camisa e tênis da senhora em vinho.
- Ponto anunciado com o motivo abaixo: quatro toques, toque duplo, bola no chão/fora, saque dentro da quadra, erro de saque ou bloqueio de saque. Motivo transmitido junto do evento de ponto.
- Comemoração entre humanos online no lobby e entre pontos: aproximar as mãos produz uma união visual breve e som de palma. Intervalo entre sons evita repetição. Desativada durante o rally.

Preservados: mapas indoor/praia, física online, saque na mão correta, seleção 2v2/4v4, velocidades, três toques dos aliados, assistência de recepção e levantamento, quatro emojis e retirada do Daily Challenge.

Verificações: oito conjuntos de regressão do código nativo; novos testes em duas bases de memória para salto, saque, pontuação e comemoração; leitura das sete malhas com índices, normais e pesos válidos; inicialização de 15 segundos do executável. O pacote verifica instalação, repetição, restauração, atualização da v14 e rejeição de arquivos incompatíveis/corrompidos.

Ainda precisa de teste real no Quest 3 e de partida entre dois PCs. Os testes automatizados usam chamadas simuladas do motor e não comprovam animações ou conforto em VR. A comemoração é reconhecida localmente usando as posições das mãos já sincronizadas pelo jogo; latência pode mudar o instante do som em cada PC.

Instalação: Caioba-completo-v15-checkpoint.zip. Todos na sala precisam da v15; salas v14 ficam separadas. Aceita jogo original compatível ou v14. O ZIP v14 foi preservado. Para voltar, execute Restaurar.cmd e instale o ZIP v14.

Fontes: output/volleyball-mod. Arte: assets/caioba-v15. Novos sistemas: celebration_v15.c. Geradores: create_caioba_characters_v15.py e raise_net_v15.py. Distribuição: package_complete_v15.py. Backup anterior completo: versions/v14-antes-cartoon. Não regenerar os mapas com scripts antigos.
