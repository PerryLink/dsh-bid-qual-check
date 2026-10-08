# dsh-bid-qual-check — Verificação do registo de condições de qualificação do concorrente

`dsh-bid-qual-check` lê um registo de condições de qualificação do concorrente —a 投标人资格条件核对表, com o seu cabeçalho mais uma linha por condição— e verifica o fecho interno desse próprio registo: se cada condição regista o seu requisito, se fica registada a situação real do concorrente, se a prova documental é anexada, se o veredicto vem do seu vocabulário, se uma partida eliminatória regista em conjunto situação, prova e veredicto, se o registo indica o seu projeto e o seu concorrente, se os números de condição são únicos e se não resta nenhum marcador de modelo por substituir na coluna do requisito.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma linha tem vazias tanto a coluna `资格条件` como a `要求内容`. Isso é reportado? | Sim. `BQ-001` exige que cada linha traga pelo menos uma dessas duas colunas e assinala a linha quando ambas estão vazias. Verifica que algo foi escrito, não se essa condição é lícita ou se deveria ter sido estabelecida — isso é uma análise do próprio caderno de encargos. |
| Uma condição tem a coluna `投标人情况` vazia e também não traz `证明材料`. | Dois achados: `BQ-002` assinala a linha pela `投标人情况` (`actual`) vazia e `BQ-003` pela `证明材料` (`evidence`) vazia. Ambas verificam apenas que a célula está preenchida, não que a situação satisfaça a condição nem que o documento seja válido, esteja em vigor ou coincida com o original, o que exige os originais e a decisão da comissão. Uma coluna presente com todas as células vazias continua a ser assinalada linha a linha; se o material não tiver essa coluna, as regras passam a `skipped` em vez de passarem em silêncio. |
| A coluna `核对结论` está vazia numa linha. O `BQ-004` reporta isso? | Não: o `BQ-004` só examina os valores escritos e ignora as células vazias. A sua lista `values` vem vazia, por isso de fábrica a regra declara-se em `skipped`; depois de configurar em `values` o vocabulário da sua instituição (`符合` / `不符合` / `需澄清`, por exemplo), cada valor fora dessa lista é assinalado linha a linha. Verifica que o valor está no seu vocabulário, não que a conclusão esteja correta, e nenhum valor invalida uma proposta. A regra está limitada a `info`, porque o vocabulário é fixado pela sua instituição. |
| Uma linha tem `是` em `是否否决项`, mas falta-lhe `投标人情况` ou `证明材料`. | O `BQ-005` exige que toda a linha cujo `是否否决项` coincida com os valores configurados (`是`, `Y`, `yes`, `true`, `否决项`, `√` por omissão) preencha em conjunto `投标人情况`, `证明材料` e `核对结论`, e assinala o que faltar. Que condições são eliminatórias depende inteiramente do caderno de encargos e dessa coluna, nunca de uma lista incorporada. Se nenhuma linha tiver essa marca, a regra declara-se em `skipped` em vez de passar, e nunca decide se a proposta deve ser rejeitada. |
| O cabeçalho do registo traz o número do concurso, mas não o projeto nem o concorrente. | O `BQ-006` reporta o cabeçalho uma vez e indica o que falta: `project` (o nome do projeto) ou `bidder` (o nome do concorrente). Verifica apenas que o cabeçalho declara essas duas partes; não revê o número do concurso nem a data da verificação, e acrescentar o vocabulário das conclusões a esta regra não ajudaria, porque quem o controla é o `values` do `BQ-004`. |
| Este registo foi copiado de um modelo: duas linhas partilham o número `3` e uma célula `要求内容` ainda diz `待填`. | O `BQ-007` assinala o `序号` repetido (a comparação ignora espaços, pelo que `3` e ` 3 ` são o mesmo número) e, se nenhuma linha tiver número, declara-se em `skipped` em vez de passar. O `BQ-008` assinala o marcador residual em `要求内容` —`【`, `】`, `{{`, `}}`, `XXX`, `待填`, `待补充`, `TBD`, `示例` e o resto da sua lista `terms`, que pode restringir. Ambas as verificações são literais: nenhuma julga se o requisito está correto, e um requisito copiado à letra que contenha `XXX` também é assinalado. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《中华人民共和国招标投标法》 | 1999年8月30日通过，2017年12月27日修正（全国人大常委会《关于修改〈中华人民共和国招标投标法〉、〈中华人民共和国计量法〉的决定》），本法自2000年1月1日起施行 | BQ-001, BQ-002, BQ-003, BQ-004, BQ-006, BQ-007, BQ-008 |
| 《中华人民共和国招标投标法实施条例》 | 国务院令第613号（2011 年 12 月 20 日公布，2017 年 3 月 1 日修订，自 2012 年 2 月 1 日起施行） | BQ-005 |

**Boundary:** this plugin checks a **投标人资格条件核对表** for the closed loop a checklist can be held to —
that every condition records its requirement and the bidder's actual position, that evidence is attached, that
verdicts come from your vocabulary, that a **pass/fail item** records all three, that the table names its
project and bidder, that numbers are unique, and that no placeholder survives. It does **not** decide whether a
bidder is qualified, whether qualification fails, or whether a bid should be rejected. **That is the
qualification committee's call, made against the evidence originals and the tender document's conditions.**

> ### ⚠️ Read this before trusting a citation in the report
>
> **Every `excerpt` in this plugin's rule pack says, in so many words, that the clause text was not
> obtained.** The regime lives in 《中华人民共和国招标投标法》(notably its articles on qualification
> conditions and on bidders' qualifications), 《招标投标法实施条例》, and **each tender document's own
> qualification conditions**. The verification pass could not retrieve verbatim clause text, so rather than
> paraphrase a quotation the pack states the gap in the `excerpt` field itself and puts the honest reasoning
> in `note`. Every rule is therefore `warn` or `info`, and a test asserts that no rule claims a quotation it
> does not have. **When the texts are in hand, two things must be done: replace each `excerpt` with the real
> clause, and raise `kind` to `direct`.**
>
> Two judgements are yours, not the plugin's. **Which conditions count as pass/fail items depends entirely on
> the tender document**, so `BQ-005` reads the **checklist's own 是否否决项 column** rather than any built-in
> list, and the values that mark an item as pass/fail are configurable. And the **verdict vocabulary ships
> empty** — with nothing configured, `BQ-004` reports itself in `skipped`. A finding never says a bid is
> invalid; it says a cell is empty or a value is not in your vocabulary.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-bid-qual-check
dsh --profile <name> --dump-config | grep 'dsh-bid-qual-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/bid-qual-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-bid-qual-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-bid-qual-check contributors.
