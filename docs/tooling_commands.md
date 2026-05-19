# Comandos de Apoio

## Qt Designer

Gerar Python a partir de um arquivo `.ui`:

```bash
pyuic5 "nome do frame".ui -o "nome do frame".py -x
```

Gerar Python a partir de um arquivo `.qrc`:

```bash
pyrcc5 "nome da imagem".qrc -o "nome da imagem".py
```

## Empacotamento

Instalar a dependencia de build:

```bash
pip install -r requirements-build.txt
```

Gerar executavel oficial com o `.spec` do projeto:

```bash
.\tools\empacotar.ps1
```

Ou manualmente:

```bash
python -m PyInstaller --noconfirm --clean cspdv.spec
```

Gerar installer com `Inno Setup`:

```bash
.\tools\gerar_installer.ps1
```
