---
name: rough-cut
description: >-
  Produz um corte bruto conservador de gravações brutas: corta ar morto, remove digitação/cópia
  de código sem fala e resolve retakes, protegendo fala e resultados de demo. Use para primeira
  passada, "tira os silêncios", "enxuga este vídeo", limpeza de gravação ou extração de clipes.
  Salva manifesto de edição reutilizável (edit.json) e transcrição mapeada; pode continuar para
  overlay-graphics na mesma execução. Legendas, B-roll e publicação ficam com outras skills.

---

# Rough Cut (corte bruto)

Entrega uma primeira passada assistível, mantendo ritmo natural e a resolução da fonte.
Na dúvida entre fala ou retake, **mantenha e sinalize**. O script cuida da mecânica; seu julgamento
vai para a edição. O master nunca é tocado: tudo sai como arquivo novo.

## Entradas e destinos

- Resolva os arquivos brutos e a pasta do projeto. Só pergunte se não houver arquivo disponível.
- Classifique o material como `talking-head` ou `screen-share`. Material misto: use análise de
  screen-share para proteger resultados de demo e avalie os trechos de talking-head separadamente.
- Ordene `_intro` primeiro, clipes do corpo na ordem natural, `_outro`/`_outtro` por último
  (case-insensitive). O script implementa isso e rejeita candidatos ambíguos a intro/outro.
- Um `endcard.mp4` pré-gravado passa direto, sem análise. Outros clipes já editados: marque com
  `--passthrough /caminho/absoluto.mp4`.
- Trabalhe em `projetos/<NNN. slug>/trabalho/rough-cut/`; entregue em `edicoes/<NNN. slug>/<nome>_rough.mp4`.
- `/tmp` é para experimentos descartáveis, nunca o único lar de um corte ou transcrição.

## 1. Analisar uma vez

Requer Python com `faster-whisper` (a `.venv` do projeto: `npm run instalar`), ffmpeg/ffprobe.
Rode com `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`).

```bash
.venv/bin/python .devin/skills/rough-cut/scripts/pipeline.py analyze \
  "/abs/parte_01.mp4" "/abs/parte_02.mp4" \
  --mode talking-head --work "projetos/<NNN. slug>/trabalho/rough-cut"
```

Isso extrai áudio mono de cada original, transcreve com tempo por palavra (faster-whisper,
modelo `large-v3-turbo`; idioma padrão `pt`, use `--language en` ou `--language auto` para outros), detecta silêncios e mede atividade de tela
dentro das pausas relevantes. Resultado: `analysis.json` + `suggested-decisions.json`. Nada é
cortado automaticamente. Janelas de screen-share sem fala mas com tela ativa vão para uma lista
`classify`, não para `cuts`.

**Leia [references/editing-rules.md](references/editing-rules.md) antes de decidir cortes.**
Consolida as regras de proteção de fala, retake, ruído e atividade aprendidas em produção.

Confira o threshold e a contagem de silêncios. Em screen-share, valide a detecção de atividade
contra um trecho conhecido de digitação/scroll antes de confiar num zero:

```bash
.venv/bin/python .devin/skills/rough-cut/scripts/pipeline.py activity /abs/fonte.mp4 --start 12 --end 16
```

Use `--threshold -35` só se a inspeção justificar; o padrão adapta ao áudio.

## 2. Decidir a edição

Copie as sugestões para `decisions.json` na primeira execução; preserve e edite as decisões
existentes em revisões. Leia transcrição e intervalos candidatos juntos.

- **Corte entrada de código sem fala.** Quem assiste não quer ver digitação/cola silenciosa.
  Resolva cada item `classify` comparando um quadro do início e do fim: código entrando num editor
  vira `cuts`; resultado aterrissando (build, teste, resposta de app/modelo) sai da lista e fica
  no vídeo. `build` se recusa a rodar enquanto a lista não estiver vazia. Narração por cima da
  digitação sempre fica.
- **Retakes são decisão editorial**, dentro de cada clipe-fonte. Mantenha a última take completa
  e genuína, incluindo o intervalo no corte da take anterior. Narração repetida de demo não é
  retake. Registre os timestamps de cada grupo e a take escolhida no relatório.
- Inspecione bordas incertas **ouvindo fatias curtas da fonte**, não re-transcrevendo tudo.
- Fillers e tosses não têm detector automático: aplique só eventos confirmados seguindo as regras
  de referência. Reporte "não analisado" quando não houve essa passada.
- Mudanças de velocidade entram em `speeds` agora, antes dos gráficos — só onde áudio acelerado e
  trabalho de tela continuam apropriados. Entrada de código sem fala é **cortada**, não acelerada.

## 3. Construir a timeline compartilhada

```bash
.venv/bin/python .devin/skills/rough-cut/scripts/pipeline.py build \
  --analysis "projetos/<NNN>/trabalho/rough-cut/analysis.json" \
  --decisions "projetos/<NNN>/trabalho/rough-cut/decisions.json" \
  --fps 30000/1001 --out "projetos/<NNN>/trabalho/rough-cut/edit.json"
```

Use a taxa de quadros pretendida (o exemplo não é obrigatório). O script mescla cortes
intersectantes, valida intervalos, trata multi-clipe e speed changes, e grava `edit.json` +
`transcript.output.json` (transcrição já no relógio da saída — ouro para overlays depois).
Intervalos são quantizados em quadros inteiros. Confira `boundary_words_for_review` ouvindo;
palavras flagradas cruzam bordas de corte e não são deletadas nem arrastadas silenciosamente.

[references/pipeline.md](references/pipeline.md) define o schema de decisões, cache, mapeamento
de timestamps e limitações. **Nunca edite `edit.json` na mão** — mude `decisions.json` e refaça o build.

## 4. Renderizar e verificar

```bash
.venv/bin/python .devin/skills/rough-cut/scripts/pipeline.py render \
  --manifest "projetos/<NNN>/trabalho/rough-cut/edit.json" \
  --out "edicoes/<NNN. slug>/<nome>_rough.mp4"
```

Encode H.264 por hardware é o padrão no Mac; `--encoder software` se indisponível (reporte o
fallback). Render usa a fonte original nas dimensões nativas e cacheia partes — revisar o
primeiro trecho não re-renderiza o resto.

**Ouça** as emendas de retake, trims de ponta e bordas de palavras. **Assista** os cortes de
screen-share. Projete duração, resolução e fps contra o manifesto. Reporte: duração original vs
final, silêncios removidos, cortes de digitação, resultados mantidos, retakes resolvidos, o que
precisa de revisão.

## 5. Continuar para overlay-graphics

Se o pedido incluir gráficos por cima, invoque `overlay-graphics` na mesma execução passando
`edit.json` e `transcript.output.json`. Os dois arquivos ficam separados: o `_rough.mp4` nunca é
sobrescrito pela versão com gráficos (`_gfx.mp4`). Pule quando o pedido for só o corte, quando a
edição parou numa ambiguidade editorial, ou quando outro orquestrador já vai chamar essa etapa.

Se o corte mudar depois, refaça o manifesto e rode os gráficos contra o **novo** ID de manifesto;
posicionamentos do ID antigo são inválidos.

## O que esta skill NÃO faz

- Legendas e shorts verticais (`shorts`), gráficos sobre o vídeo (`overlay-graphics`),
  thumbnails (`thumbnail`), teasers (`teaser`).
- Apagar ou reescrever o master — impossível por contrato.

Histórico de lições em [references/history.md](references/history.md).
