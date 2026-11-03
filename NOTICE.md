# NOTICE — atribuições de terceiros

O Studio é distribuído sob [MIT](LICENSE). Esta central concentra a proveniência dos
componentes incorporados de projetos de terceiros. Manter este arquivo preserva as licenças
originais sem espalhar nomes pela documentação.

## Skills adaptadas (MIT)

As skills `rough-cut`, `shorts`, `overlay-graphics`, `teaser`, `code-animation`, `thumbnail` e
`podcast-edit` foram adaptadas do repositório público de skills de **Dan Vega**
(`github.com/danvega/skills`, licença MIT). O conteúdo foi reescrito em português, generalizado
(paths, ferramentas e fluxos deste repositório) e liberado de integrações específicas do autor
original. A licença MIT exige apenas a preservação do aviso — este arquivo é esse aviso.

## Blocos HyperFrames (Apache 2.0)

`.devin/skills/code-animation/assets/blocks/` (`code-diff.html`, `code-typing.html`,
`code-morph.html`) são cópias intactas do registry do **HyperFrames (HeyGen)**, licenciados sob
Apache 2.0. `LICENSE` e `UPSTREAM.md` na própria pasta documentam a origem e a versão pinada
(`hyperframes@0.7.77`).

## Outros componentes

- `remotion-best-practices` e pacote `hyperframes-*`: instalados via `npm run instalar` a partir
  de `remotion-dev/skills` e `heygen-com/hyperframes` (skills vendoradas, não versionadas aqui).
- Plugin `watch` (`.claude/settings.json`, opcional): `bradautomates/claude-video`, MIT.
- `tools/transcrever.py` e `fw_whisper.py`: usam [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (MIT).
