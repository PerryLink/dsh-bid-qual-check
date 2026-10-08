# dsh-bid-qual-check — Verificación del registro de condiciones de cualificación del licitante

`dsh-bid-qual-check` lee un registro de condiciones de cualificación del licitante —la 投标人资格条件核对表, con su cabecera más una fila por condición— y comprueba el cierre interno de ese propio registro: que cada condición registre su requisito, que quede registrada la situación real del licitante, que se adjunte la prueba documental, que el veredicto proceda de su vocabulario, que una partida eliminatoria registre a la vez situación, prueba y veredicto, que el registro nombre su proyecto y su licitante, que los números de condición sean únicos y que no quede ningún marcador de plantilla sin sustituir en la columna del requisito.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una fila tiene vacías tanto la columna `资格条件` como la `要求内容`. ¿Se informa de eso? | Sí. `BQ-001` exige que cada fila traiga al menos una de esas dos columnas y señala la fila cuando ambas están vacías. Comprueba que se haya escrito algo, no si esa condición es lícita o si debería haberse establecido: eso es un examen del propio pliego. |
| Una condición tiene vacía la columna `投标人情况` y tampoco trae `证明材料`. | Dos hallazgos: `BQ-002` señala la fila por la `投标人情况` (`actual`) vacía y `BQ-003` por la `证明材料` (`evidence`) vacía. Ambas comprueban solo que la celda esté rellena, no que la situación satisfaga la condición ni que el documento sea válido, esté vigente o coincida con el original, lo que exige los originales y la decisión de la comisión. Una columna presente con todas sus celdas vacías se sigue señalando fila por fila; si el material no trae esa columna, las reglas pasan a `skipped` en lugar de pasar en silencio. |
| La columna `核对结论` está vacía en una fila. ¿Lo señala `BQ-004`? | No: `BQ-004` solo examina los valores escritos y omite las celdas vacías. Su lista `values` viene vacía, así que de fábrica la regla se declara a sí misma en `skipped`; cuando configure en `values` el vocabulario de su institución (`符合` / `不符合` / `需澄清`, por ejemplo), cada valor fuera de esa lista se señala fila por fila. Comprueba que el valor esté en su vocabulario, no que la conclusión sea correcta, y ningún valor invalida una oferta. La regla está limitada a `info`, porque el vocabulario lo fija su institución. |
| Una fila lleva `是` en `是否否决项`, pero le falta `投标人情况` o `证明材料`. | `BQ-005` exige que toda fila cuya celda `是否否决项` coincida con los valores configurados (`是`, `Y`, `yes`, `true`, `否决项`, `√` por defecto) rellene a la vez `投标人情况`, `证明材料` y `核对结论`, y señala lo que falte. Qué condiciones son eliminatorias depende por completo del pliego y de esa columna, nunca de una lista incorporada. Si ninguna fila lleva esa marca, la regla se declara en `skipped` en lugar de pasar, y nunca decide si la oferta debe rechazarse. |
| La cabecera del registro trae el número de licitación, pero no el proyecto ni el licitante. | `BQ-006` informa una vez de la cabecera y nombra lo que falta: `project` (el nombre del proyecto) o `bidder` (el nombre del licitante). Solo comprueba que la cabecera declare esas dos partes; no revisa el número de licitación ni la fecha de verificación, y añadir el vocabulario de conclusiones a esta regla no serviría, porque lo controla el `values` de `BQ-004`. |
| Este registro se copió de una plantilla: dos filas comparten el número `3` y una celda `要求内容` todavía dice `待填`. | `BQ-007` señala el `序号` repetido (la comparación ignora los espacios, así que `3` y ` 3 ` son el mismo número) y, si ninguna fila lleva número, se declara en `skipped` en lugar de pasar. `BQ-008` señala el marcador residual en `要求内容` —`【`, `】`, `{{`, `}}`, `XXX`, `待填`, `待补充`, `TBD`, `示例` y el resto de su lista `terms`, que puede acortar. Ambas comprobaciones son literales: ninguna juzga si el requisito es correcto, y un requisito copiado al pie de la letra que contenga `XXX` también se señala. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-bid-qual-check
dsh --profile <name> --dump-config | grep 'dsh-bid-qual-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/bid-qual-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-bid-qual-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-bid-qual-check contributors.
