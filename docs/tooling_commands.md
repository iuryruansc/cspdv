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

Gerar executavel com `pyinstaller`:

```bash
pyinstaller --onefile --noconsole "nome do arquivo que sera convertido".py
```
