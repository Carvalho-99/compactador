# Compactador de Arquivos

Cria um arquivo `.zip` individual para cada arquivo dentro de uma pasta selecionada.

Ideal para compactar vídeos, fotos ou qualquer conjunto de arquivos separadamente, sem precisar fazer um por um manualmente.

---

## Download

Baixe o executável pronto na pasta [`dist/`](dist/Compactador.exe) — não precisa instalar Python.

> **Windows 64-bit** · Sem dependências externas

---

## Como usar

1. Execute `dist/Compactador.exe` (ou dê dois cliques em `ABRIR_COMPACTADOR.bat`)
2. Clique em **Procurar** e selecione a pasta com os arquivos
3. Escolha as opções desejadas:
   - **Incluir subpastas** — processa arquivos dentro de subdiretórios também
   - **Apagar original após compactar** — remove o arquivo original depois de zipar (use com cuidado)
4. Clique em **COMPACTAR TUDO**
5. Acompanhe o progresso em tempo real na barra e no log

Cada arquivo vira um `.zip` com o mesmo nome na mesma pasta.  
Exemplo: `video01.mp4` → `video01.zip`

---

## Exemplo

```
📁 Minha Pasta
├── video01.mp4        →   video01.zip
├── video02.mp4        →   video02.zip
├── video03.mp4        →   video03.zip
└── ...
```

---

## Compilar você mesmo

Requer Python 3.10+ e PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Compactador" compactador.py
```

O executável será gerado em `dist/Compactador.exe`.

---

## Tecnologias

- Python 3.14
- `zipfile` (built-in)
- `tkinter` (interface gráfica)
- PyInstaller (geração do `.exe`)
