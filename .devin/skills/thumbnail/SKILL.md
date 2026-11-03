---
name: thumbnail
description: >-
  Desenha thumbnails variadas para YouTube com fotos reais do apresentador, recortes transparentes
  e composições HTML/CSS por conceito, renderizadas com Chrome headless. Use para "faz uma
  thumbnail", "capa do vídeo", "testa opções de capa". Não trata de: hooks e títulos (decisão
  editorial do plano), edição de vídeo (rough-cut/overlay-graphics), criação do zero (hyperframes).

---

# Thumbnail

Composição com fotos reais + HTML/CSS. Mantenha a pessoa reconhecível e o tipo nítido.
Escolha primeiro a história visual; templates são atalhos de implementação, não o briefing
criativo. Um fundo novo atrás da mesma pose e do mesmo bloco de texto **não é** uma direção nova.
Fotos de estúdio inteiras são assets válidos, não só recortes transparentes.

## Arquivos e assets

```
templates/hero-right.html     wordmark + pill + chips à esquerda, pessoa à direita
templates/versus.html         dois cards + selo VS, para comparativos
templates/before-after.html   painel linha-X-vermelha → linha-check-verde + selo de hook
templates/big-type-light.html fundo claro, tipo escuro gigante
templates/big-shield.html     objeto-herói gigante + tipo empilhado, sem pessoa
templates/merge-button.html   UI de produto falsa como herói (card + botão + cursor)
templates/quote-card.html     uma citação em tamanho máximo numa moldura fina
templates/annotated-code.html janela de IDE + elipse/seta de marcador vermelho + nota
templates/file-explorer.html  árvore de arquivos com UM arquivo circulado em vermelho

scripts/render.sh             renderiza cada HTML em PNG 1920x1080 (~1–3s cada; Google Chrome, Chromium
                              ou o Chromium do playwright; sai com 1 se algum falhar)
scripts/contact_sheet.py      uma folha estilo feed: cada opção a 360px com o título + cópia a
                              120px. É o passo de verificação E a peça de apresentação.
scripts/photo_sheet.py        seletor paginado de fotos/recortes, com índice de paths numerado
scripts/cutout.swift          recorte de sujeito via Apple Vision (macOS):
                              swift cutout.swift <entrada> <saida.png>
```

Biblioteca de assets (crie uma vez, reaproveite sempre): sugira `assets/thumbnail/cutouts/`
(recortes PNG transparentes nomeados `<expressao>-<look>.png` + `manifest.md` +
`cutouts-sheet.png`), `assets/thumbnail/photos/` (fotos originais) e `assets/thumbnail/doodles/`
(setas/círculos desenhados). Nos drafts, aponte o `src` das imagens para um path absoluto
(`file:///Users/.../assets/thumbnail/cutouts/x.png`): os templates trazem `assets/thumbnail/...`
relativo, que quebra quando o draft vive em `trabalho/thumb/`. Os scripts Python usam Pillow
(instalado na `.venv` por `npm run instalar`).

Rascunhos ficam em `projetos/<NNN. slug>/trabalho/thumb/`; só a vencedora final vai para
`edicoes/<NNN. slug>/thumbnail.png` (+ `.html` do lado, para revisões futuras).

## Fluxo

### Rodada 0: fixar a promessa

Trave a **promessa** (o que o vídeo entrega), não o template nem a expressão. O texto da
thumbnail não repete o título — os dois leem juntos. Se a promessa estiver vaga, resolva com a
pessoa antes de desenhar.

### Conferir o histórico e a biblioteca

Antes de escolher conceitos, leia [references/creative-range.md](references/creative-range.md).
Revise as últimas thumbnails já usadas (pasta `edicoes/`) e marque famílias de pose repetidas em
`trabalho/thumb/selecao.md`. Abra o seletor de fotos **e** o de recortes; reconstrua se faltar:

```bash
.venv/bin/python .devin/skills/thumbnail/scripts/photo_sheet.py assets/thumbnail/photos -o assets/thumbnail/photo-picker
```

Escolha por gesto, olhar, emoção e potencial de crop antes de roupa. Uma versão com roupa
diferente da MESMA pose de apontar não é repertório novo.

### Rodada 1: três ou quatro opções de verdade

1. **Escolha histórias visuais.** Cada opção defende a mesma promessa com argumento visual
   diferente (esforço desproporcional, alternativa mais simples, fronteira de decisão). Uma
   frase por opção antes de abrir template. A lista de estruturas abaixo é exemplo, não menu.
2. **Escale a foto.** Pose/família diferente por direção com rosto; olhar e gesto apontam para
   o objeto focal. Considere confiança calma, ceticismo e fotos naturais, não só surpresa.
   Nem todo rosto precisa ficar no terço direito.
3. **Componha cada opção.** Adapte um template ou crie HTML/CSS novo. Limpe foto de exemplo,
   selos e código do template antes de adicionar o seu. Regras para toda opção:
   - Um único ponto focal dominante; cor serve à hierarquia.
   - **4 palavras ou menos** no total legível — chips, labels e código contam como texto.
   - Nada sobre o rosto; tipo livre da cabeça do recorte.
   - Tamanho/posição do rosto por história: close, esquerda, centro, reação pequena ou ausente.
   - Logos só quando identificam o assunto real. Nada de sparkle de IA automático.
4. **Renderize numa chamada** (sequencial; NÃO paralelize o Chrome — ele deixa de sair):

   ```bash
   .devin/skills/thumbnail/scripts/render.sh draft-*.html
   ```

5. **Monte UMA folha e leia** — verificação e teste de encolhimento na mesma imagem:

   ```bash
   .venv/bin/python .devin/skills/thumbnail/scripts/contact_sheet.py \
     -o round1.png -t "<título candidato>" draft-*.png
   ```

   Um `-t` por imagem. Na folha: nada clipado, nada tocando o rosto, hierarquia clara, ideia
   principal ainda lê na cópia de 120px. E **alcance**: ignorando cor e copy, se as opções têm a
   mesma posição de rosto, silhueta e relação com o objeto, troque um conceito ANTES de
   apresentar. Corrija e re-renderize até passar.
6. **Salve, mostre, pare.** PNGs + HTML em `trabalho/thumb/` como `thumb-v1-<conceito>.png`.
   Registre fontes, diferenças e status em `selecao.md`. Mostre a folha, recomende uma com o
   tradeoff. A pessoa escolhe e diz o que está errado.

### Rodada 2: apertar a vencedora

Só as variantes que respondem ao feedback: expressão (outra pose), copy (palavras do hook ou
qual leva o acento), ou **um** movimento de composição (lado, tamanho do herói, crop). Um
movimento por take. Feedback "mesma coisa/chato" → reabra o conceito, não troque roupa.
Empate entre dois títulos → ambos na folha.

### Fechamento

1. Copie a vencedora para `edicoes/<NNN. slug>/thumbnail.png` + `.html`.
2. Atualize `selecao.md` (foto/recorte usado, família de pose, composição, data).

**Troca de rosto primeiro.** Gostou da thumbnail mas não da foto → troque o `src` do recorte e
re-renderize (segundos). Edição manual fora disso é exceção.

## Lista de estruturas (dispositivos de herói)

Varie composição e argumento visual, não só paleta:

- **ui-artifact** (`merge-button.html`): UI de produto falsa como herói; o momento do clique/decisão.
- **file-explorer** (`file-explorer.html`): árvore com UM arquivo circulado — hooks "o que É esse arquivo".
- **story-panel** (`before-after.html`): linha X-vermelho → check-verde.
- **hand-drawn** (`annotated-code.html` ou SVG à mão sobre fundo escuro): círculos e setas de marcador.
- **terminal escuro** (`hero-right.html`, `versus.html`): fundo escuro + tipo grande branco — "cara da casa" opcional, compete como qualquer direção.
- **code-panel** (`annotated-code.html` sem o adesivo): o hook é uma linha de código gigante, um token em acento.
- **big-object** (`big-shield.html`): um objeto gigante como herói, pessoa pequena ou ausente — quando o hook É um objeto.
- **quote-card** (`quote-card.html`): uma fala em tamanho máximo — só quando o hook é uma citação.
- **clean-light** (`big-type-light.html`): fundo de papel, tipo escuro enorme — quando campo claro serve ao conceito.
- **photo-editorial**: foto de estúdio, crop deliberado, tipo mínimo — expressão carrega o argumento.
- **scale-metaphor**: esforço/aposta via relação objeto grande/pequeno. Documento/UI ilustrativo
  claramente conceitual — nunca invente resultados medidos nem finja screenshot de produto real.

## Novo recorte

**De qualquer foto** (fundo liso ajuda):

```bash
swift .devin/skills/thumbnail/scripts/cutout.swift foto.jpg expressao-look.png
```

**Do bruto deste vídeo** (a roupa combina com o vídeo; expressões vêm de graça):

```bash
ffmpeg -i bruto.mp4 -vf "fps=1/5,scale=480:-1" -q:v 4 frames/f_%03d.jpg   # folha para escolher
ffmpeg -ss <t> -i bruto.mp4 -frames:v 1 frame.png
swift .devin/skills/thumbnail/scripts/cutout.swift frame.png expressao-look.png
```

Cuidado com motion blur e boca no meio da palavra — ajuste o `-ss` em 0.1s até o quadro ficar
nítido. Todo keeper entra em `assets/thumbnail/cutouts/` com nome padrão, linha no `manifest.md`
e `cutouts-sheet.png` reconstruída com `photo_sheet.py`. Recorte que fica só na pasta do projeto mata a biblioteca.

## Tokens de design (direção terminal-escuro)

Valem só para esse look; outras direções definem a própria paleta e mantêm a disciplina de texto.

- Fundo: gradiente escuro `linear-gradient(135deg, #0c1a10, #08120b, #060d08)` + brilhos radiais
  suaves. Escuro o bastante para tipo branco peso 900 carregar.
- Acento `#6cd97e`; bordas `#3f7a4d`; texto mutado `#9fc7a8`.
- Tipo: Inter/SF 800–900, tracking apertado, text-shadow para profundidade.
- Recorte: ancorado embaixo, ~85–90% da altura do quadro, drop-shadow forte. Erre para grande.

## Regras

- Folha de contato antes de apresentar — sempre. É o teste de legibilidade de verdade.
- Nunca repita o título na imagem; nunca texto sobre rosto.
- Todo render gera arquivo novo; originais de foto e master do vídeo intocados.
- Assets externos só locais ou gerados — nada de download/stock silencioso.
