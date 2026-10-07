/**
 * dsh-bid-qual-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'bid_qual_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  seq: ['序号', '条件序号', '编号', 'seq'],
  criterion: ['资格条件', '资格要求', '评审因素', 'criterion'],
  category: ['类别', '条件类别', '分类', 'category'],
  required: ['要求内容', '标准要求', '要求', 'required'],
  actual: ['投标人情况', '实际情况', '证明材料摘要', 'actual'],
  evidence: ['证明材料', '证明文件', '页码', 'evidence'],
  verdict: ['核对结论', '结论', '是否符合', 'verdict'],
  isPassFail: ['是否否决项', '否决项', '是否通过性', 'isPassFail'],
  checkedBy: ['核对人', '复核人', 'checkedBy'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'criteria', '资格条件'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '招标项目名称'],
  tenderNo: ['tenderNo', '招标编号', '项目编号'],
  bidder: ['bidder', '投标人', '投标单位名称'],
  checkedAt: ['checkedAt', '核对日期'],
  verdicts: ['verdicts', '结论口径'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '资格条件',
  'criterion',
  '要求内容',
  'required',
  '投标人情况',
  'actual',
  '证明材料',
  'evidence',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
