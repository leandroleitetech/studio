# Primeiros passos

Este tutorial leva você do zero até a primeira edição. Leva uns 20 minutos, a maior parte esperando instalações.

---

## 1. O que você precisa

| Item | Para quê | Obrigatório? |
|---|---|---|
| Um **agente de IA** que rode comandos e leia arquivos — **Devin CLI** (`devin`) é o recomendado; Claude Code, Codex e Cursor também funcionam | é o seu diretor de vídeo | sim |
| **Node.js** (versão LTS) | roda o Remotion | sim |
| **Python** 3.10 ou mais novo | transcrição local | sim |
| **FFmpeg** | lê e converte vídeo; é o que a skill `assistir` usa para "ver" o vídeo | sim |
| **Git** | baixar e atualizar este repositório | recomendado |

Com o **Devin CLI**, basta abrir o terminal na pasta do projeto e rodar `devin`. Ele lê o `AGENTS.md`, as skills de `.devin/skills/` e a configuração de `.devin/` automaticamente.

## 2. Instalar os programas

### Windows

Abra o **PowerShell** e rode, um por vez:

```powershell
winget install --id OpenJS.NodeJS.LTS --exact
winget install --id Python.Python.3.12 --exact
winget install --id Gyan.FFmpeg --exact
winget install --id yt-dlp.yt-dlp --exact
winget install --id Git.Git --exact
```

Feche e abra o PowerShell de novo e confira:

```powershell
node --version
python --version
ffmpeg -version
```

### macOS

Instale o [Homebrew](https://brew.sh) e rode:

```bash
brew install node python ffmpeg yt-dlp git
```

## 3. Baixar o Studio e instalar tudo

### Jeito fácil: peça ao agente

Abra o seu agente de IA (Devin CLI: `devin` no terminal) e cole:

```text
Instala o repositório https://github.com/leandroleitetech/studio na pasta ~/dev (siga a seção "Instalação" do README).
```

Ele clona e instala tudo (dependências, transcrição local, skills e navegadores headless) e confere com `npm run verificar`. Quando terminar, **abra uma sessão nova** do agente dentro da pasta `studio`: skills novas só aparecem numa sessão nova.

### Jeito manual

Escolha uma pasta **fora** do OneDrive, iCloud ou Dropbox (a sincronização atrapalha o render). Por exemplo, `C:\dev` no Windows ou `~/dev` no Mac.

```bash
cd ~/dev
git clone https://github.com/leandroleitetech/studio.git
cd studio
npm run instalar
```

O `npm run instalar` faz tudo de uma vez: dependências do Remotion e o navegador que ele usa para renderizar, a `.venv` com transcrição local (`faster-whisper`) e Pillow (`requirements.txt`), as skills `remotion-best-practices` e o pacote `hyperframes` (para Devin, Claude Code, Codex e Cursor, só dentro do projeto) e as dependências das skills do estúdio. No fim ele roda `npm run verificar` e mostra o que deu certo e o que falta. Rode `npm run verificar` sempre que quiser conferir a instalação.

Sem Git? Baixe o ZIP pelo botão verde **Code → Download ZIP** no GitHub, descompacte e rode `npm run instalar` dentro da pasta.

Teste o Remotion:

```bash
npm run studio
```

Abre uma página no navegador com os exemplos da galeria. Se você vê as composições em `Estilos` e consegue dar play, está tudo certo. Feche com `Ctrl+C` no terminal.

## 4. Sobre as skills

Skills são pacotes de conhecimento que o agente carrega quando precisa. Este repositório usa:

- **`assistir`** (`.devin/skills/assistir/`): já vem no projeto. Ensina o agente a "ver" o vídeo extraindo quadros com `ffmpeg` e lendo as imagens — funciona em qualquer agente que leia `SKILL.md`, sem custo e sem conta externa;
- **`remotion-best-practices`**: boas práticas do Remotion ([remotion-dev/skills](https://github.com/remotion-dev/skills)), instalada pelo `npm run instalar` para todos os agentes detectados;
- **pacote `hyperframes`** ([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)): ~20 skills para **criar vídeos do zero** em HTML+GSAP — motion graphics, legendas embutidas, recortes de talking-head, vídeos de música, slideshows — também instaladas pelo `npm run instalar`.

> Usa o **Claude Code**? Existe ainda o plugin opcional `watch` ([bradautomates/claude-video](https://github.com/bradautomates/claude-video)), declarado mas **desligado por padrão** em `.claude/settings.json` (é código de terceiro — revise antes de ativar). Ele é redundante com a `assistir` — use um ou outro.

## 5. Transcrição: local e sem chaves

O `tools/transcrever.py` roda o [faster-whisper](https://github.com/SYSTRAN/faster-whisper) num ambiente Python do projeto (`.venv`, criada pelo `npm run instalar`): gratuito, offline depois do primeiro download do modelo (~1,6 GB) e com o tempo exato de cada palavra — que é o que sincroniza as animações e os cortes com a fala. O agente chama via `npm run transcrever`. Nenhuma chave de API é necessária.

---

## 6. Entendendo as pastas

```text
studio/
├─ AGENTS.md           o "diretor": instruções que o agente lê ao abrir o projeto
├─ .devin/             configuração do Devin: permissões e skills do projeto
├─ README.md           visão geral
├─ guias/              os manuais (você está aqui)
├─ estilos/            galeria de estilos de referência, com imagens
│
├─ projetos/           ← VOCÊ COLOCA AQUI o vídeo e os prints
│  └─ 001. meu-video/
│     ├─ video/        o vídeo gravado, bruto ou cortado (nunca é alterado)
│     ├─ prints/       prints e imagens do que você quer ver animado
│     ├─ assets/       logo, fontes, fotos e referências visuais
│     ├─ frames/       (gerado) quadros que o agente "assistiu"
│     ├─ transcricao/  (gerado) texto com o tempo de cada palavra
│     ├─ trabalho/     (gerado) intermediários: cortes, gráficos, áudio
│     └─ plano.md      (gerado) o plano de edição que você aprova
│
├─ edicoes/            ← AQUI SAI o vídeo pronto
│  └─ 001. meu-video/
│
├─ src/                código do Remotion
│  ├─ Root.tsx         lista de vídeos registrados
│  ├─ videos/          uma subpasta por vídeo seu
│  ├─ estilos/         código dos exemplos da galeria
│  └─ _shared/         peças reaproveitadas
├─ tools/              transcrição local
└─ scripts/            instalar, verificar e checagens automáticas
```

Regra de bolso: **você só mexe em `projetos/`** (para entregar material) **e em `edicoes/`** (para pegar o resultado). O resto é trabalho do agente.

A pasta `projetos/` inteira fica fora do Git (`.gitignore`), com exceção do exemplo. Assim, seus vídeos e prints não vão parar no GitHub por acidente se você publicar um fork.

## 7. Sua primeira edição

1. Crie a pasta `projetos/001. meu-video/video/` e coloque seu vídeo lá (MP4 ou MOV; bruto ou já cortado).
2. Crie `projetos/001. meu-video/prints/` e salve prints de tudo o que você cita no vídeo: sites, notícias, telas de ferramentas.
3. Abra a pasta `studio` no seu agente (Devin CLI: rode `devin` dentro dela).
4. O agente vai perguntar o que você quer fazer: **editar** um vídeo gravado, **cortar/extrair** trechos ou **criar** um vídeo do zero. Responda.
5. Diga o que quer. Exemplo:
   ```text
   Edita o projeto 001. Quero o vídeo completo, estilo minimal suíço, cortando os silêncios longos.
   ```
6. Aprove (ou ajuste) o plano de edição que ele apresentar.
7. Confira os quadros de revisão que ele mostrar.
8. Pegue o vídeo em `edicoes/001. meu-video/`.

Não sabe o que pedir? Pergunte ao próprio agente: "o que dá para fazer com esse vídeo?". Ele foi instruído a sugerir opções.

## 8. Glossário rápido

| Termo | Significado |
|---|---|
| **Master** | o seu vídeo gravado, a base de tudo (nunca é alterado) |
| **Inserção** | qualquer elemento que entra por cima ou no lugar da câmera |
| **Overlay** | inserção com fundo transparente, que fica por cima do vídeo |
| **B-roll** | imagens de apoio em tela cheia enquanto você continua falando |
| **Split / tela dividida** | conteúdo de um lado, câmera do outro |
| **PiP** (picture-in-picture) | câmera pequena num canto |
| **Push-in / punch-in** | zoom lento / zoom rápido na câmera |
| **Gatilho** | a palavra falada que faz uma inserção aparecer |
| **Render** | gerar o arquivo de vídeo final |
| **Still** | um quadro parado exportado como imagem, usado para revisão |
| **Skill** | um pacote de instruções que ensina o agente a fazer uma tarefa |
| **Jump cut** | corte seco dentro da mesma cena, que "pula" o tempo — típico de Reels |
| **EDL** | "edit decision list": a lista de cortes que um editor segue |
