# Volley Riot

Vôlei em VR com aparência cartoon, equipes fáceis de reconhecer e comemoração social rápida. O nome remete à energia de uma partida entre amigos. É um nome criativo de trabalho; não foi feita análise de registro de marca.

## Identidade

Azul royal `#2468DF`, vermelho coral `#E74750`, azul-marinho `#10233F` e creme `#FFF5DC`. A fonte Lilita One dá personalidade aos menus, placares e mensagens. Logo próprio com bola, letras robustas e movimento diagonal. O vermelho corresponde ao lado negativo do eixo da quadra e o azul ao positivo.

As superfícies usam contraste amplo, sem depender de detalhes pequenos para reconhecer um time. A bola e as linhas permanecem legíveis contra os dois lados do piso. Antenas listradas são decorativas.

## Jogo e assistência

- O limite junto à rede considera a cabeça rastreada e deixa a mesma margem de 12 cm nos dois lados, compensando o deslocamento dentro da área física de VR.
- No levantamento com os dois GRABs, o alvo fica a 85 cm da rede, dentro do próprio lado. A posição lateral acompanha a bola e fica limitada a 3,5 m do centro para evitar alvos fora da antena.
- Bots usam a zona próxima da rede quando levantam no segundo toque. A recepção inicial continua preparando o levantador.
- A assistência de recepção vale para o primeiro contato de cada posse do time. Segundo e terceiro contatos não recebem essa mesma ajuda.
- Bots ficam 10% mais altos visualmente. O cabelo comprido recebe volume contínuo na nuca, sem alterar o rosto ou os óculos.

## Mãos e interação social

Luvas de formas arredondadas, cinco dedos articulados, tecido creme, punho marinho e detalhe azul/vermelho. A geometria nova utiliza o esqueleto já conectado às animações. Dois GRABs ativam a pose aberta de levantamento, inclusive antes de tocar na bola.

High five usa as posições das mãos sincronizadas, funciona durante a partida e toca uma palma com retorno tátil local. Aproximar as mãos a menos de 22 cm pode ativá-lo. É preciso separá-las novamente, e há um intervalo de 0,7 s para evitar repetição. A comemoração não reposiciona controles nem colisores.

## Menu online

Resume e Leave continuam disponíveis. Change Teams agenda a troca para o próximo ponto, preservando o rally atual. O host verifica a capacidade do time, remove os bots antigos e transmite as novas posições. Um time cheio exibe “Time lotado”.

O seletor percorre quatro combinações de emoji e terno: Cool, Nerd, Chill e Wild. A escolha aparece no botão e é enviada aos outros jogadores da mesma versão. A seleção é da sessão; não há loja ou desbloqueio.

As salas usam `VolleyRiot-2v2-v16` e `VolleyRiot-4v4-v16`. Todos os participantes precisam instalar o mesmo pacote e escolher modo, região e sala correspondentes. A mensagem e os botões que convidavam ao Discord são removidos.

## Placar e ginásio

O placar apresenta vermelho à esquerda e azul à direita, independentemente do time de quem olha. No ginásio, dois painéis grandes, um em cada parede de fundo, acompanham os pontos da partida. Faixas de proteção, acabamentos nas cores das equipes e antenas dão unidade ao espaço.

A notificação de ponto usa uma chamada curta, “Vermelho +1” ou “Azul +1”, e o motivo em uma segunda linha menor. O texto ocupa menos espaço que a apresentação anterior.

## Direção para a próxima revisão visual

O arquivo `DESIGN.html` permite revisar a identidade, o menu, o placar e a seleção de skins. É uma maquete de apresentação; a validação final de tamanho, distância e leitura deve ocorrer dentro do headset. Critérios de aceite: ler o placar do fundo da quadra, alcançar os quatro botões sem inclinar o corpo e não encobrir a bola com o aviso de ponto.

## Validação e limites

Os testes executam o código compilado em um emulador de CPU com substituições explícitas para Unity e Photon. Eles verificam decisões, argumentos, posições, contagem de contatos e comportamento ao realocar o programa na memória. A abertura do executável testa carregamento dos arquivos. Essas verificações não substituem uma partida em VR nem uma sessão real entre dois computadores.
