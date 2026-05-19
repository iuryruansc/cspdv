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
