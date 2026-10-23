# Caioba — fontes do mod

Checkpoint v15 para Volleyball Fever, Steam build 9216628. Consulte [CHECKPOINT-V15.md](CHECKPOINT-V15.md) para mudanças, testes e validação VR pendente.

`spin_mod.c` reúne `mode_2v2.c`, `formation_serve.c`, `online_2v2.c`, `comfort_v14.c` e `celebration_v15.c`. `build_patch.py` aplica o código compilado à cópia local compatível. `test_*.py` verificam comportamento com chamadas simuladas do motor.

`create_caioba_characters_v15.py` cria os sete bots cartoon, quatro emojis e rede. Arte própria em `assets/caioba-v15/`; a versão anterior permanece em `assets/caioba-v14/`. Os modelos usam o esqueleto e animações existentes na instalação local.

`raise_net_v15.py` eleva rede e colisores em 40 cm. `package_complete_v15.py` cria e verifica o instalador completo, com atualização da v14. Mapas: indoor v11 e praia v12 (`build_beach_v12.py`).

A v15 adapta salto, saque e levantamento à rede elevada, corrige o spawn sobre o bot sacador, mostra o motivo do ponto e adiciona comemoração por contato das mãos no lobby online e entre pontos.

O repositório contém fontes e arte própria do mod. É necessária uma instalação própria do jogo compatível. Binários, arquivos extraídos, backups, ferramentas, arte Mikasa e ZIPs permanecem locais. Os scripts dependem das pastas locais `working`, `backup`, `versions` e `tools`; não há build a partir de um clone vazio.

Testes automatizados e inicialização aprovados. Partida VR e sessão real entre dois PCs ainda pendentes nesta versão. Todos na sala precisam da v15.
