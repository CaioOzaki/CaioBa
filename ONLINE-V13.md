# Correcao online v13

Fisica de giro habilitada em 2v2 e 4v4 online. O giro calculado no toque aceito viaja no campo de contexto da RPC confiavel existente; cada cliente decodifica antes de executar as regras originais. Componentes quantizados com erro maximo aproximado de 0,24 rad/s. Predicao local e corpo principal recebem o mesmo giro e integracao limitada a 30 Hz.

O saque no gatilho aceita apenas Hand que descende do PhysicalBody do NetworkPlayer.localInstance. Os avatares remotos tambem tem Hand e leem o input local; antes podiam consumir o pedido de saque e prender a bola no avatar errado. Conferida a hierarquia dos prefabs locais. Funciona em ambos os formatos online.

Namespace Photon v13 separa clientes antigos. TODOS precisam instalar Caioba-completo-v13.zip. Instalador aceita o pacote v12 anterior e preserva backup. Texturas e mapas permanecem os da v12.

Validacao: emulacao do codigo compilado em dois enderecos ASLR, transporte codificado/decodificado entre dois estados de cliente, mesma trajetoria e predicao nos dois formatos; toque rejeitado nao aplica giro; testes de maos local/remota e gatilho; regressao de menus, bots, recepcao e regras. Instalador testado com jogo original e upgrade v12, idempotencia, restauracao e rejeicao de corrupcao. Executavel permaneceu ativo 15 s e carregou IndoorArenaScene. Ainda requer nova partida VR entre dois PCs.

Backup do codigo anterior: versions/v12-antes-online-fisica. Nenhuma publicacao nova no GitHub realizada nesta etapa.
