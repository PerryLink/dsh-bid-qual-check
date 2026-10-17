import { readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

describe('rule-pack evidence paths', () => {
  it('every referenced evidence file exists', () => {
    const root = new URL('..', import.meta.url).pathname
    const yaml = readFileSync(join(root, 'rules/bid-qual-check.yaml'), 'utf8')
    const refs = [...yaml.matchAll(/rules\/evidence\/([A-Za-z0-9._-]+\.md)/g)].map(m => m[1] as string)
    expect(refs.length).toBeGreaterThan(0)
    for (const ref of new Set(refs)) {
      expect(existsSync(join(root, 'rules/evidence', ref)), ref).toBe(true)
    }
  })

  it('does not claim a direct excerpt is missing', () => {
    const yaml = readFileSync(new URL('../rules/bid-qual-check.yaml', import.meta.url), 'utf8')
    const blocks = yaml.split(/\n\s*-\s+id:\s+/).slice(1)
    for (const block of blocks) {
      if (/kind:\s*direct/.test(block)) expect(block).not.toContain('本次未取得明文条号')
    }
  })
})
