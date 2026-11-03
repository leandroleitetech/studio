---
name: briefing
description: >-
  Ponto de partida de qualquer trabalho no Studio: entrevista curta que transforma "quero
  fazer um vídeo" num projeto pronto — objetivo, material disponível (vídeos, prints, logos,
  referências), formato e estilo, scaffold da pasta do projeto em projetos/ com plano.md, e
  roteamento para a skill certa (edição por cima, cortes, shorts, teaser, thumbnail, trilha,
  criação do zero). Use no início de sessões, quando a pessoa diz "quero editar/criar um vídeo",
  "por onde começo", "nova edição", ou quando o pedido chega sem contexto de material/formato.
  Não edita nem renderiza — prepara e roteia.
---

# Briefing (do "quero fazer um vídeo" ao projeto pronto)

Esta skill é a recepção do estúdio. Seu trabalho é descobrir o essencial — uma decisão por
vez, sem interrogar — e deixar o projeto montado e roteado. Linguagem simples: a pessoa pode
nunca ter editado nada.

## Princípio

Pergunte o mínimo para escolher o **modo** e o **material**. Assuma padrões sensatos para o
resto e diga quais assumiu. Sempre termine dizendo o próximo passo.

## As 5 perguntas (na ordem, uma por vez)

1. **O que você quer entregar?** → define o modo:
   - vídeo longo editado / aula / YouTube → **edição por cima** (Remotion) ou **com cortes** (rough-cut)
   - Reels/Shorts/TikTok de um vídeo maior → `shorts` (clipes) ou edição vertical
   - trailer/teaser → `teaser`
   - vídeo novo sem gravação (promo, explainer, anúncio) → **criação do zero** (HyperFrames/Remotion)
   - só thumbnails, só trilha, só limpar áudio → `thumbnail` / `soundtrack` / `podcast-edit`
2. **O que você já tem?** → o inventário de material:
   - vídeo(s) gravado(s)? onde estão? (traga para `projetos/<NNN. slug>/video/`)
   - prints do que é citado na fala? (sites, telas, dados → `prints/` — vale ouro)
   - logo, fontes, cores da marca? referências de estilo (links, outros vídeos)?
   - para criação do zero: roteiro, página do produto, música, design no Figma?
3. **Formato e plataforma:** 16:9 (YouTube), 9:16 (Reels/Shorts/TikTok), quadrado/4:5 (feed)?
   Duração-alvo? (isso já limita densidade e ritmo)
4. **Estilo e intensidade:** cite 2–3 da [galeria](../../../estilos/README.md) que combinam com o
   assunto; intensidade `sutil` / `equilibrada` / `dominante`.
5. **O que é sagrado?** o que não pode faltar (uma frase, um dado) e o que não pode aparecer
   (termos, frames, cortes proibidos). Isso evita retrabalho.

## Montar o projeto

```text
projetos/<NNN. slug>/
├─ video/        ← gravações (intocáveis depois de entrar)
├─ prints/       ← screenshots para animar
├─ assets/       ← logo, fontes, referências visuais
├─ trabalho/     ← intermediários (cortes, gfx, audio) — nunca entregável
└─ plano.md      ← nasce aqui, aprovado antes de produzir
```

- Numeração: `NNN` = maior número existente + 1, três dígitos (`001. meu-video`).
- Se o material ainda não existe (vai gravar), diga o que falta e por quê — e só.
- Crie o `plano.md` inicial com: objetivo, público, formato, material disponível/faltando,
  modo escolhido, ideias de abordagem. Ele é o contrato de aprovação.

## Roteamento (depois do material resolvido)

| Pedido | Skill |
|---|---|
| assistir/entender o vídeo | `assistir` (sempre antes de planejar edição) |
| enxugar, tirar silêncios, resolver retakes | `rough-cut` |
| textos/gráficos por cima do vídeo | `overlay-graphics` ou composição Remotion (`src/videos/`) |
| extrair verticais | `shorts` |
| trailer | `teaser` |
| animar código (diff/digitação) | `code-animation` |
| capa | `thumbnail` |
| trilha/SFX por código | `soundtrack` |
| limpar/normalizar áudio de podcast | `podcast-edit` |
| vídeo novo do zero | `hyperframes` (roteador) ou Remotion |

## Regras

- Uma decisão por vez; padrões assumidos são declarados, não escondidos.
- Se a pessoa trouxer tudo de uma vez ("quero um Reels do vídeo X com legenda"), pule o que já
  está respondido — o intake serve a pessoa, não o formulário.
- Sem material e sem ideia clara? Proponha 2–3 direções depois de olhar `projetos/` e `estilos/`.
- Nada é renderizado nesta fase. Termine com: projeto criado + próximo passo + o que a pessoa
  pode pedir agora.
