# Caioba — fontes do mod

Checkpoint v14 para Volleyball Fever, Steam build 9216628. Consulte [CHECKPOINT-V14.md](CHECKPOINT-V14.md) para mudanças, testes e pontos que ainda precisam de partida VR.

`spin_mod.c` reúne `mode_2v2.c`, `formation_serve.c`, `online_2v2.c` e `comfort_v14.c`. `build_patch.py` aplica o código compilado à cópia local compatível. `test_*.py` executam verificações específicas.

`create_caioba_characters.py` cria desenhos e geometrias procedurais próprios dos sete bots, quatro emojis e rede. Os PNGs próprios estão em `assets/caioba-v14/`. Os modelos usam o esqueleto e animações existentes do jogo na instalação local.

`raise_net_v14.py` aumenta a rede e os colisores em 40 cm. `package_complete_v14.py` cria e verifica o instalador completo. Mapas atuais: indoor v11 e praia v12 (`build_beach_v12.py`).

O repositório contém fontes e arte própria do mod. Para executar, é necessária uma instalação própria do jogo compatível. Binários, arquivos extraídos, backups, ferramentas, arte Mikasa e ZIPs de instalação permanecem locais. Os scripts dependem das pastas locais `working`, `backup`, `versions` e `tools`; não há build a partir de um clone vazio.

Validação automatizada e inicialização aprovadas; partida VR e sessão real entre dois PCs ainda pendentes nesta versão.
