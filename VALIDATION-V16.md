# Validação do candidato v16

Os relatórios em `validation/v16/` acompanham o código desta versão.

- **Jogabilidade compilada:** 136 casos para limite da rede, deslocamento físico da cabeça, recepção em cada nova posse e alvo do levantamento dos bots, executados em dois endereços de carga.
- **Comemoração:** aproximação das mãos sincronizadas, intervalo entre palmas, reativação depois da separação e disponibilidade durante o rally. A comemoração não move mãos ou colisores.
- **Menu e placares:** criação única dos botões, eventos próprios, escolha de skin, troca no próximo ponto, remoção dos bots anteriores e atualização dos dois placares com a ordem vermelho/azul.
- **Regressão online:** namespace da versão, inicialização dos clientes, formatos, distribuição de jogadores, guarda para time cheio e falta de saque de jogador remoto. Chamadas de Unity e Photon são substituídas explicitamente nesses testes.
- **Instalador real em cópias isoladas:** original → v16, instalação repetida, restauração repetida, v15 rostos → v16, restauração após atualização e recusa de entrada incompatível antes de modificar outros arquivos. ZIP e deltas têm verificação de integridade.
- **Arquivos Unity:** reabertura dos assets serializados e leitura dos componentes nativos modificados. O ginásio carregou na abertura sem renderização.
- **Menu escuro v16.2:** 45 controles e 225 estados de cor verificados nos arquivos salvos, com contraste mínimo de 7,95:1. Fonte nativa idêntica à versão funcional anterior; ações dos botões preservadas e cores guardadas pelo CurvedUI sincronizadas. Atualização e restauração das versões v16 e v16.1 exercitadas pelo instalador. A confirmação visual no headset continua pendente.

## Pendências de integração

A tentativa de iniciar uma partida automaticamente sem headset não avançou pelo menu. Não houve partida em VR, conferência visual dentro do headset ou sessão real entre dois computadores. Os testes com chamadas substituídas não comprovam latência, animação percebida ou sensação da assistência em uma partida real.

Por isso o pacote é identificado como **versão de teste**, com instalador reversível. Os amigos precisam ter a instalação compatível e usar exatamente o mesmo pacote, formato, região e sala.
