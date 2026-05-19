# Empacotamento

## Objetivo

O empacotamento oficial do projeto usa `PyInstaller` com um arquivo `.spec`, em vez de depender apenas de um comando solto `--onefile`.

Esse fluxo prepara o executavel para:

- iniciar por [main.py](D:\Python\cspdv\main.py)
- carregar `.env` externo ao lado do executavel
- incluir `media/` no bundle
- continuar usando caminhos gravaveis fora do bundle para:
  - imagens copiadas para `media/produtos`
  - backups

## Estrategia de caminhos

O projeto agora separa:

- `resource_root`
  - arquivos empacotados no bundle
- `app_root`
  - pasta externa da aplicacao, ao lado do `.exe`

Implementacao central:

- [runtime_paths.py](D:\Python\cspdv\utils\runtime_paths.py)

Regras principais:

- `.env` e lido preferencialmente em `app_root/.env`
- `media/` empacotado pode ser lido como recurso
- novos arquivos gerados pelo sistema devem ir para `app_root`

## Arquivos do build

- [cspdv.spec](D:\Python\cspdv\cspdv.spec)
- [empacotar.ps1](D:\Python\cspdv\tools\empacotar.ps1)
- [gerar_installer.ps1](D:\Python\cspdv\tools\gerar_installer.ps1)
- [CSPdv.iss](D:\Python\cspdv\installer\CSPdv.iss)
- [.env.example](D:\Python\cspdv\.env.example)

## Como gerar

Instale a dependencia de build:

```powershell
pip install -r requirements-build.txt
```

No PowerShell, dentro da pasta do projeto:

```powershell
.\tools\empacotar.ps1
```

Ou manualmente:

```powershell
python -m PyInstaller --noconfirm --clean cspdv.spec
```

## Como gerar o installer

Depois de gerar o executável, instale o Inno Setup 6 e rode:

```powershell
.\tools\gerar_installer.ps1
```

Resultado esperado:

- `dist-installer/Setup_CSPdv.exe`

Melhorias do installer atual:

- sincroniza `APP_NAME` e `APP_VERSION` a partir de [.env.example](D:\Python\cspdv\.env.example)
- cria atalhos
- copia `.env.example`
- cria `.env` se ele ainda nao existir
- pode abrir o `.env` automaticamente ao final da instalacao
- pode abrir a pasta de instalacao ao final da instalacao

## Resultado esperado

O executavel sera gerado em:

- `dist/CSPdv.exe`

## Arquivos que devem acompanhar a entrega

Minimo recomendado:

- `CSPdv.exe`
- `.env`

Se a operacao precisar editar ou reaproveitar imagens fora do bundle, tambem e valido manter ao lado do executavel:

- `media/`

## Observacoes

- o usuario do MySQL ainda precisa ter acesso ao servidor configurado
- o sistema cria automaticamente o banco configurado se ele nao existir
- depois aplica migrations e seeds no startup
- o instalador copia `.env.example` e cria `.env` se ele ainda nao existir
