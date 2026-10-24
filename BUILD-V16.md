# Build do Volley Riot v16

Alvo: Windows x64, Unity 2019.4.5f1, Volleyball Fever Steam build 9216628. O pipeline usa a instalação própria com o pacote **v15 rostos** como referência dos assets. As verificações de hash interrompem o empacotamento se essa base não corresponder.

Não é um projeto Unity completo. O repositório contém o código e a arte do mod. DLLs do jogo, metadata, assets extraídos, backups e pacotes de distribuição ficam fora do Git.

## Preparação local

1. Instale `requirements-v16.txt` em um ambiente Python.
2. Defina `VOLLEY_RIOT_GAME_DIRECTORY` com a pasta da instalação v15, caso não esteja no local Steam padrão.
3. Coloque a **GameAssembly.dll original compatível** em `backup/GameAssembly.dll` e uma cópia em `working/GameAssembly.dll`. O pacote v15 permite recuperar essa DLL pelo delta reverso e seu hash.
4. Gere as DummyDll da metadata local com Il2CppDumper e coloque-as em `tools/dump/DummyDll`. Elas são usadas somente para reconstruir a estrutura dos componentes serializados.
5. Crie `analysis/`, `working/` e `tools/` se necessário. Use um compilador Clang ou Zig que gere PE x64 sem dependências externas. A validação desta versão usou Zig 0.13.0.

## Código nativo

Compilação equivalente usada no Windows:

```text
zig cc -target x86_64-windows-msvc -O2 -shared -nostdlib -fno-stack-protector -DPATCH_DELTA=0x194f000 spin_mod.c -o tools/spin-native.dll '-Wl,--entry,DllMain' '-Wl,--image-base,0x180000000'
python build_patch.py
```

O montador verifica imports, endereço-base, instruções substituídas, seções, realocações e informações de desenrolamento de pilha. Uma base incorreta interrompe o build.

## Assets, testes e pacote

```text
python build_assets_v16.py
python build_metadata_v16.py
python stage_native_v16.py
python test_volley_riot_v16.py
python test_v16_gameplay.py
python test_v16_online_menu.py
python test_menu_visibility_v16.py
python test_hooks.py
python test_online_2v2.py
python package_volley_riot_v16.py --game "PASTA-DA-INSTALACAO-V15" --candidate visuals-v16 --v15-package "PASTA-OU-ZIP-DA-V15-ROSTOS"
python test_v16_installer.py
```

O pacote aceita o jogo original compatível e a v15 rostos, verifica todos os arquivos antes de aplicar e guarda backup da operação. Para gerar a atualização v16.1 sobre a v16, acrescente `--upgrade-from versions/v16-before-menu-fix` ao empacotador, usando uma cópia verificada dos dois arquivos anteriores nessa pasta. `Restaurar.cmd` retorna os onze arquivos ao original. Os arquivos de distribuição não devem ser commitados no repositório.

`MODE_PROBE` habilita controles de diagnóstico somente em uma cópia descartável. `stage_native_v16.py` rejeita esse tipo de binário para impedir sua distribuição.

## O que a validação cobre

Os testes de CPU executam o código compilado em dois endereços de carga e substituem explicitamente Unity/Photon. Eles verificam os limites da rede, elegibilidade de recepção, alvo dos bots, ciclo do high five, botões, mensagens de skin, troca ao fim do ponto e placares. O instalador é exercitado em uma cópia isolada, incluindo instalação, atualização, repetição e restauração.

A abertura sem renderização carregou o ginásio em Unity. A tentativa de iniciar uma partida automaticamente sem headset não avançou pelo menu; portanto ela não valida uma partida solo. A conferência visual em VR e a sessão online real entre dois computadores continuam pendentes antes de tratar o pacote como uma versão estável.
