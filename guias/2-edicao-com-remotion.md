# Edição de vídeo gravado com Remotion (gratuito)

Neste fluxo, o agente assiste ao seu vídeo, entende o que você fala e **programa** a edição: animações com o [Remotion](https://www.remotion.dev) (uma ferramenta que transforma código em vídeo) e, quando você pede, **cortes com o ffmpeg** (remover silêncios, reordenar, acelerar, extrair clipes). Você não precisa saber programar: você conversa, aprova o plano e confere o resultado.

**Custo:** zero. Tudo roda no seu computador.
**Ferramentas:** skill `assistir` (extrai quadros do vídeo com ffmpeg — vem em `.devin/skills/`), `tools/transcrever.py` (tempo de cada palavra), skill `remotion-best-practices`, `ffmpeg`/`ffprobe` para cortes e o próprio Remotion.

Para criar um vídeo **sem master** (do zero), a skill `hyperframes` se auto-roteia — este guia não é necessário. Se você nunca mexeu com Remotion, leia antes o [manual do Remotion para leigos](3-manual-remotion.md).

---

## O que você entrega

1. O vídeo em `projetos/<NNN. nome>/video/` — já cortado, ou bruto se você quiser que o estúdio corte antes (veja "Edição com cortes").
2. **Prints** de tudo o que você quer ver animado em `projetos/<NNN. nome>/prints/`: páginas, notícias, telas de ferramentas, logos, gráficos. Este é o ponto que mais melhora o resultado. Uma animação feita em cima de um print real é sempre mais fiel e mais bonita que uma recriação.
3. Suas **orientações** em texto livre: estilo desejado (veja a [galeria](../estilos/README.md)), formato (horizontal ou vertical), o que não pode faltar, o que evitar.

Dica: dê nomes claros aos prints (`noticia-openai.png`, `tela-configuracoes.png`). O agente usa o nome para saber onde cada um entra.

## O que você recebe

Um de dois entregáveis (o agente pergunta se não estiver claro):

- **Vídeo completo** (padrão): um MP4 final com câmera, animações, telas divididas e prints, com o áudio original.
- **Inserções separadas:** arquivos soltos para você montar no seu editor. Overlays transparentes em `.mov` (ProRes 4444, com canal alpha) e telas cheias em `.mp4`, mais uma lista de timecodes.

Tudo vai para `edicoes/<NNN. nome>/`.

---

## O processo, passo a passo

O agente conduz estas fases na ordem e **para nos pontos de aprovação**.

### 1. Organizar

- Localiza a pasta nova em `projetos/`. Se você só soltou um vídeo lá, ele cria `projetos/<NNN>/video/` e move o arquivo para dentro.
- Numeração: três dígitos, ponto e espaço (`001. meu-video`). Novo projeto = maior número existente + 1.
- Roda `ffprobe` no vídeo para registrar duração, resolução, fps e codecs no topo do `plano.md`.
- Cria `edicoes/<NNN. nome>/`.

### 2. Assistir e transcrever

1. **Quadros e visão geral (skill `assistir`):** o agente segue as instruções da própria skill (`.devin/skills/assistir/SKILL.md`): extrai mosaicos e quadros com `ffmpeg` para `<projeto>/frames` e lê as imagens para mapear enquadramento, posição do rosto, fundo e luz. (No Claude Code, o plugin `watch` cumpre o mesmo papel.)
2. **Tempo por palavra (local e gratuito):**
   `npm run transcrever -- "<vídeo>" "<projeto>/transcricao"`
   (usa o Python da `.venv` criada pelo `npm run instalar`; idioma padrão `pt` — acrescente `en` ou `auto` no fim para outro)
   Gera `palavras.json` (início e fim de cada palavra) e `transcript.md`.
   Atenção: depois de uma pausa, o início da **primeira** palavra pode vir adiantado (até ~1 s). Antes de ancorar um gatilho nela, confira ouvindo ou use o fim da palavra.
3. Nomes próprios mal transcritos podem ser corrigidos no texto ("cloud" → Claude) sem mexer nos tempos.
4. Com o conteúdo entendido, a pasta ganha um nome descritivo: `001. meu-video`.

### 3. Planejar (ponto de aprovação)

O agente escreve `plano.md` usando a [direção editorial](4-direcao-editorial.md):

- leitura do vídeo e suas orientações;
- estilo escolhido e intensidade;
- cenas do repertório que entram (e as que ficam de fora, com o porquê) e a curva de energia;
- para vídeos com mais de ~3 min: mapa macro (blocos e cena dominante de cada um);
- tabela: `# | início–fim | cena | entrada | gatilho (palavra @ tempo) | visual | print usado`;
- zona do rosto a preservar, tirada dos quadros reais.

Veja um plano real em [projetos/000. exemplo/plano.md](../projetos/000.%20exemplo/plano.md).

**Nada é programado antes de você aprovar o plano.**

### 4. Programar as cenas

- O código do vídeo fica em `src/videos/<slug>/` e é registrado em `src/Root.tsx` dentro de um `<Folder>`.
- Os arquivos de `projetos/` são acessados com `staticFile('<NNN. nome>/...')` (a pasta `projetos` é a pasta pública do Remotion).
- **Vídeo completo:** uma única instância contínua de `<Video>` com o master; a câmera muda de tamanho e lugar animando o contêiner, nunca reiniciando o vídeo. Dimensões e fps herdados do master.
- **Tela dividida:** use sempre `src/_shared/synchronized-split.tsx`. Ele garante que câmera e painel entrem e saiam juntos. O `npm run typecheck` bloqueia splits feitos à mão.
- Toda animação depende de `useCurrentFrame()`. Nada de transições ou animações CSS.
- Tempos definidos em segundos (vindos do `palavras.json`) e convertidos com o fps.
- `<Sequence premountFor={fps}>` em toda cena com tempo definido.
- Evite `TransitionSeries.Transition` na timeline do master: a sobreposição encurta o vídeo.
- Os exemplos em `src/estilos/` mostram como cada estilo da galeria foi construído. Use como ponto de partida, não como molde fixo.

### 5. Conferir (ponto de aprovação)

1. `npm run typecheck`.
2. Stills (quadros parados) no início, no meio e no fim de cada mudança de layout:
   `npx remotion still src/index.ts <Composicao> edicoes/<NNN. nome>/stills/q0450.png --frame=450`
3. O agente revisa: rosto coberto? texto legível? borda preta? print cortado? marca-texto no lugar? E mostra os stills principais para você aprovar antes do render.
4. Você também pode assistir tudo em tempo real com `npm run studio` (abre no navegador).

### 6. Renderizar e entregar

- **MP4 final:**
  `npx remotion render src/index.ts <Composicao> "edicoes/<NNN. nome>/<nome>-final.mp4" --codec=h264 --crf=17`
- **Overlay transparente:**
  `npx remotion render src/index.ts <Composicao> "edicoes/<NNN. nome>/<nome>-overlay.mov" --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444`
- Validação com `ffprobe`: resolução, fps, duração igual à do master, uma única trilha de áudio (e canal alpha nos `.mov`).
- O agente informa o caminho do arquivo, duração, resolução, codecs e timecodes (se forem inserções).
- Apaga só os intermediários que ele mesmo criou. Seu vídeo e seus prints nunca são apagados.

---

## Edição com cortes (quando você pede)

Por padrão o master é intocável. Quando você pede cortes — "tira os silêncios", "enxuga para 5 minutos", "faz um short desse trecho" — o agente usa as skills de corte, que entregam **arquivos novos** em `edicoes/`:

- **`rough-cut`** (`.devin/skills/rough-cut/`): transcreve, detecta silêncios e digitação sem fala, propõe cortes e retakes num `decisions.json` que você pode revisar, gera um manifesto (`edit.json`) e renderiza `<nome>_rough.mp4` + a transcrição já no relógio do vídeo cortado (`transcript.output.json`).
- **`shorts`**: extrai verticais 9:16 com legenda palavra a palavra da versão cortada.
- **`podcast-edit`**: o equivalente só para áudio (MP3 + SRT).

Depois dos cortes, o fluxo segue igual: as animações são compostas **por cima da versão cortada**, usando `transcript.output.json` no lugar do `palavras.json` (o master original continua intacto em `video/`).

---

## Pedidos que funcionam bem

```text
Edita o projeto 001. Estilo minimal suíço, vídeo completo em MP4.
```

```text
Quero só as inserções do projeto 002: overlays em MOV e telas cheias em MP4.
Os prints estão na pasta, usa a notícia no momento em que eu falo "pesquisa".
```

```text
Faz uma versão vertical (9:16) dos primeiros 45 segundos do projeto 003,
com legenda grande palavra por palavra.
```

```text
Corta os silêncios e os "ééé" do projeto 002 e me dá uma versão enxuta,
mais os 3 melhores trechos em vertical para o Shorts.
```

```text
Muda a cena 7 do plano: em vez de tela cheia, quero o print com a câmera no canto.
```
