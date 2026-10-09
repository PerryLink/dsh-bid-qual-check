# dsh-bid-qual-check — Bidder qualification condition register check

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-bid-qual-check` reads one bidder qualification condition register — the 投标人资格条件核对表, its header plus one row per qualification condition — and checks that register's own closed loop: that each condition records its requirement, that the bidder's actual position is recorded, that evidence is attached, that the verdict comes from your vocabulary, that a pass/fail item records position, evidence and verdict together, that the register names its project and bidder, that condition numbers are unique, and that no unreplaced placeholder survives in the requirement column.

## What it looks like

![Terminal demo of dsh-bid-qual-check: real output over its BQ-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-bid-qual-check/main/docs/assets/dsh-bid-qual-check-demo.png)

Real output from this plugin over its own `BQ-002` test fixture — not a mock-up. The rule pack ships no invented quotations, so a finding names both the clause it applied and the fact that the clause text was not obtained.

## What it answers

| You ask | What it answers |
|---|---|
| One row has both `资格条件` and `要求内容` blank. Is that reported? | Yes. `BQ-001` holds every row to at least one of those two columns and reports the row when both are empty. It checks that something was written, not whether that condition is lawful or should have been set at all — that is a review of the tender document itself. |
| A condition has its `投标人情况` column empty, and no `证明材料` either. | Two findings: `BQ-002` reports the row for the blank `投标人情况` (`actual`) and `BQ-003` for the blank `证明材料` (`evidence`). Both check only that the cell is filled — not whether the position satisfies the condition, nor whether the document is valid, current or matches the original, which needs the originals and the committee's call. A column that is present with every cell blank is still reported row by row; a material without that column puts the rule in `skipped` instead of passing silently. |
| The `核对结论` column is blank on a row. Does `BQ-004` report it? | No — `BQ-004` tests only the values that are written and skips blank cells. Its `values` list ships empty, so out of the box the rule reports itself in `skipped`; once you configure your institution's vocabulary in `values` (`符合` / `不符合` / `需澄清`, say), a value outside that list is reported row by row. It checks that the value is in your vocabulary, not that the conclusion is correct, and no value ever invalidates a bid. The rule is capped at `info`, because the vocabulary is your institution's to set. |
| A row's `是否否决项` cell reads `是`, but `投标人情况` or `证明材料` is missing. | `BQ-005` requires `投标人情况`, `证明材料` and `核对结论` together on every row whose `是否否决项` cell matches the configured marks (`是`, `Y`, `yes`, `true`, `否决项`, `√` by default) and reports the row with what is missing. Which conditions count as pass/fail comes entirely from the tender document and from that column, never from a built-in list. If no row carries such a mark, the rule reports itself in `skipped` instead of passing — and it never decides whether the bid should be rejected. |
| The register's header names the tender number, but not the project or the bidder. | `BQ-006` reports the header once and names what is missing: `project` (the project name) or `bidder` (the bidder name). It only checks that the header declares those two parties — it does not check the tender number or the check date, and adding the verdict vocabulary to this rule would not help, because that is controlled by `BQ-004`'s `values`. |
| This register was copied from a template: two rows share the number `3`, and one `要求内容` cell still reads `待填`. | `BQ-007` reports the repeated `序号` (the comparison ignores whitespace, so `3` and ` 3 ` are the same number), and if no row carries a number at all it reports itself in `skipped` instead of passing. `BQ-008` reports the residual placeholder in `要求内容` — `【`, `】`, `{{`, `}}`, `XXX`, `待填`, `待补充`, `TBD`, `示例` and the rest of its `terms` list, which you can narrow. Both checks are literal: neither judges whether the requirement itself is right, and a requirement genuinely quoted with an `XXX` in it is reported too. |

## Standards it follows

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for several bidders use `ptc` |

## What it does

Registers the `bid_qual_check` tool. It reads one qualification register — the package header plus one row per
condition — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `BQ-001` | every condition records its requirement | warn | direct |
| `BQ-002` | every condition records the bidder's actual position | warn | direct |
| `BQ-003` | every condition attaches evidence | warn | direct |
| `BQ-004` | the verdict comes from your vocabulary (off by default) | info | local |
| `BQ-005` | a pass/fail item records position, evidence and verdict | warn | principle |
| `BQ-006` | the table names its project and bidder | warn | principle |
| `BQ-007` | condition numbers are unique | warn | principle |
| `BQ-008` | the requirement column holds no unreplaced placeholder | warn | principle |
## Install

```sh
dsh plugin --profile <name> add dsh-bid-qual-check
dsh --profile <name> --dump-config | grep 'dsh-bid-qual-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/bid-qual-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `BQ-004` `values` — your verdict vocabulary, e.g. `[符合, 不符合, 需澄清]`. Empty means no check.
- `BQ-005` `conditionValues` — the values in your 是否否决项 column that mark an item as pass/fail, by
  default `[是, Y, yes, true, 否决项, √]`.
- `BQ-008` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
project: 某某工程施工招标
tenderNo: ZB-2026-018
bidder: 某某建设有限公司
rows:
  - { 序号: '1', 资格条件: 施工资质等级, 要求内容: 建筑工程施工总承包二级及以上,
      投标人情况: 持有建筑工程施工总承包二级资质，证书在有效期内,
      证明材料: 资质证书复印件，资格文件第 12 页, 核对结论: 符合, 是否否决项: 是, 核对人: 李工 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/bid-qual-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`BQ-004` or `BQ-005` reports itself as skipped.** The verdict vocabulary is empty, or no row is marked as
  a pass/fail item. Both depend on your project, and the plugin will not guess them.
- **`BQ-002` fires on a condition I consider self-evident.** A blank actual-position cell means "not checked",
  which is the one thing a qualification register must never be. Record the position, even if it is obvious.
- **`BQ-005` fires on a pass/fail item missing evidence.** That is the check: a pass/fail item without all
  three records cannot be defended after the fact.
- **`BQ-008` fires on a requirement I copied verbatim.** The word `XXX` or `待填` really is in the cell.
  Narrow `terms`, or fix the register.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-bid-qual-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-bid-qual-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-bid-qual-check contributors.
