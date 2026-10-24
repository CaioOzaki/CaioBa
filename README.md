# Volley Riot — fontes do mod

Identidade cartoon e ajustes de vôlei em VR para Volleyball Fever, Steam build 9216628. O repositório continua chamado **CaioBa**; o nome apresentado no jogo passa a ser **Volley Riot**.

A v16 acrescenta quadra azul/vermelha, logo e acabamento da rede próprios, antenas decorativas, Lilita One nos placares e avisos, luvas de geometria nova e placares nas duas paredes do ginásio. Bots ficam mais altos e o personagem de cabelo comprido recebe cobertura na nuca.

A revisão **v16.2** usa botões escuros com letras claras, inclusive ao selecionar e clicar, sincroniza as cores da interface curva e usa a fonte nativa já funcional nos menus. O instalador atualiza também as versões v16 e v16.1. A física e o protocolo das salas v16 são os mesmos.

O limite junto à rede considera a cabeça rastreada. Levantamentos do jogador com dois GRABs e dos bots no segundo toque miram uma zona próxima da rede. A assistência de recepção vale para o primeiro toque de cada posse. High five funciona durante o rally, com som e retorno tátil, sem deslocar mãos ou colisores.

No menu online, **Change Teams** agenda a troca para o próximo ponto; o host verifica vagas e remonta os times. O seletor percorre quatro combinações de emoji e terno. As salas `VolleyRiot-2v2-v16` e `VolleyRiot-4v4-v16` ficam separadas da v15 e do original.

## Design e build

- [Game design](GAME-DESIGN-V16.md) e [maquete interativa](DESIGN.html).
- [Como gerar o build e o pacote](BUILD-V16.md).
- Código principal: `spin_mod.c`, `mode_2v2.c`, `formation_serve.c`, `online_2v2.c`, `comfort_v14.c`, `celebration_v15.c` e `volley_riot_v16.c`.
- Arte e licença da fonte: `assets/volley-riot-v16/`.

O pacote de distribuição é gerado separadamente e exige uma instalação própria compatível. Cada amigo deve instalar o mesmo ZIP e escolher modo, região e sala correspondentes. O instalador aceita o original e a v15 rostos, verifica os arquivos, faz backup e oferece restauração.

## Estado da validação

O código compilado é exercitado por testes com substituições explícitas para Unity e Photon, incluindo dois endereços de carga. O instalador é testado em cópias isoladas. Os resultados em `validation/v16/` registram o alcance de cada verificação.

**A v16 é uma versão de teste. Conferência em headset e sessão online real entre dois computadores ainda estão pendentes.** Os testes automatizados não medem a sensação do levantamento, a leitura da interface em VR nem a latência de uma sala real.

Arquivos extraídos do jogo, DLLs, metadata, ferramentas, backups e ZIPs ficam fora do Git. O clone vazio não contém o projeto Unity original nem todos os insumos locais do build. Os checkpoints anteriores permanecem documentados em `CHECKPOINT-V15*.md` e anteriores.
