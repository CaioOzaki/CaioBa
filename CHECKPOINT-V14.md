# Checkpoint v14 — 23/10/2026

Estado: pacote completo criado e testado; validação em partida VR pendente.

Implementado:
- Sete corpos de bots arredondados e sete aparências próprias.
- Quatro avatares de terno com emojis, distribuídos por ordem dos jogadores online.
- Texturas próprias da rede e altura aumentada em 40 cm, com colisores.
- 4v4 solo/online: velocidade 1,6x para humanos e bots aliados, 1,4x para bots sem humano no time; levantamentos altos e prioridade de três toques. Bot aliado evita bloqueio.
- Segundo toque: dois GRABs pressionados ativam levantamento assistido para um colega; soltar qualquer um desativa. Dedos abertos como feedback local.
- Daily Challenge removido do menu.
- Mantidas as correções v13 da física online e da mão correta no saque.

Verificado: código nativo em emulação com duas bases de memória, 32 cenários novos de levantamento, regressões de modo, saque, recepção e rede; leitura dos modelos, índices, normais e pesos; inicialização de 15 segundos no executável; instalador, instalação repetida, restauração, atualização v13 e rejeição de arquivos corrompidos.

Próximo teste no Quest 3: conferir deformação/visibilidade dos bots, quatro rostos entre dois PCs, gesto dos dedos, altura da rede e se os saques dos bots passam com conforto. Ainda não houve playtest VR nem teste online real desta versão. Feedback das mãos é local; não há transmissão adicional dos dedos.

ZIP: Caioba-completo-v14-checkpoint.zip. Todos na sala precisam da v14.
O ZIP v13 e o backup anterior foram preservados localmente. Restaurar.cmd volta ao original; depois é possível instalar o ZIP v13.

Retomada: fontes em output/volleyball-mod; arte em assets/caioba-v14; pacote em distribution; validações em analysis. Não sobrescrever a praia v12 com geradores de mapas antigos.
