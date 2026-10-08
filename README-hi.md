# dsh-bid-qual-check — निविदा प्रतिभागी की अर्हता शर्तों के रजिस्टर की जाँच

`dsh-bid-qual-check` निविदा प्रतिभागी की अर्हता शर्तों का एक रजिस्टर — 投标人资格条件核对表, उसका हेडर और प्रत्येक अर्हता शर्त की एक पंक्ति — पढ़ता है और उसी रजिस्टर का आंतरिक बंद-चक्र जाँचता है: क्या प्रत्येक शर्त अपनी आवश्यकता दर्ज करती है, क्या प्रतिभागी की वास्तविक स्थिति दर्ज है, क्या प्रमाण संलग्न है, क्या निर्णय आपकी शब्दावली से आता है, क्या निर्णायक मद में स्थिति, प्रमाण और निर्णय तीनों साथ दर्ज हैं, क्या रजिस्टर अपना परियोजना-नाम और प्रतिभागी बताता है, क्या शर्तों के क्रमांक अद्वितीय हैं, और क्या आवश्यकता कॉलम में कोई अपूरित प्लेसहोल्डर बचा नहीं है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| एक पंक्ति में `资格条件` और `要求内容` दोनों कॉलम खाली हैं। क्या यह दर्ज होता है? | हाँ। `BQ-001` हर पंक्ति में इन दोनों में से कम से कम एक कॉलम भरे होने की अपेक्षा करता है और दोनों खाली होने पर उस पंक्ति को दर्ज करता है। यह देखता है कि कुछ लिखा गया है या नहीं, यह नहीं कि वह शर्त वैध है या उसे रखा ही जाना चाहिए था — वह निविदा दस्तावेज़ की अपनी समीक्षा है। |
| एक शर्त का `投标人情况` कॉलम खाली है और `证明材料` भी नहीं है। | दो प्रविष्टियाँ: `BQ-002` खाली `投标人情况` (`actual`) के लिए उस पंक्ति को दर्ज करता है और `BQ-003` खाली `证明材料` (`evidence`) के लिए। दोनों केवल यह देखते हैं कि कोष्ठ भरा है या नहीं — यह नहीं कि स्थिति शर्त पूरी करती है, या दस्तावेज़ वैध, अवधि-मान्य या मूल के अनुरूप है; उसके लिए मूल दस्तावेज़ और समिति का निर्णय चाहिए। कॉलम मौजूद हो पर उसके सभी कोष्ठ खाली हों तो भी पंक्ति-दर-पंक्ति दर्ज होता है; सामग्री में वह कॉलम ही न हो तो ये नियम चुपचाप पास होने के बजाय `skipped` में चले जाते हैं। |
| एक पंक्ति में `核对结论` कॉलम खाली है। क्या `BQ-004` इसे दर्ज करता है? | नहीं — `BQ-004` केवल लिखे गए मानों की जाँच करता है और खाली कोष्ठ छोड़ देता है। इसकी `values` सूची खाली आती है, इसलिए डिफ़ॉल्ट रूप से यह नियम स्वयं को `skipped` में बताता है; `values` में अपनी संस्था की शब्दावली (जैसे `符合` / `不符合` / `需澄清`) कॉन्फ़िगर करने पर सूची से बाहर का मान पंक्ति-दर-पंक्ति दर्ज होता है। यह देखता है कि मान आपकी शब्दावली में है, यह नहीं कि निष्कर्ष सही है, और कोई मान निविदा को अमान्य नहीं करता। यह नियम `info` तक सीमित है, क्योंकि शब्दावली आपकी संस्था तय करती है। |
| एक पंक्ति में `是否否决项` में `是` लिखा है, पर `投标人情况` या `证明材料` नहीं भरा। | `BQ-005` अपेक्षा करता है कि जिस पंक्ति का `是否否决项` कॉन्फ़िगर किए गए मानों (`是`, `Y`, `yes`, `true`, `否决项`, `√` — डिफ़ॉल्ट) से मेल खाए, उसमें `投标人情况`, `证明材料` और `核对结论` तीनों भरे हों, और जो छूटा हो उसे दर्ज करता है। कौन-सी शर्तें निर्णायक हैं, यह पूरी तरह निविदा दस्तावेज़ और उसी कॉलम पर निर्भर है, किसी अंतर्निहित सूची पर नहीं। कोई पंक्ति ऐसा चिह्न न रखती हो तो यह नियम पास होने के बजाय `skipped` बताता है, और यह कभी तय नहीं करता कि निविदा अस्वीकार होनी चाहिए। |
| रजिस्टर के हेडर में निविदा क्रमांक है, पर परियोजना-नाम और प्रतिभागी नहीं। | `BQ-006` हेडर की कमी एक बार दर्ज करता है और बताता है कि `project` (परियोजना-नाम) या `bidder` (प्रतिभागी) में क्या छूटा। यह केवल देखता है कि हेडर इन दो पक्षों को घोषित करता है: निविदा क्रमांक या जाँच की तारीख की जाँच नहीं करता, और इस नियम में निष्कर्ष-शब्दावली जोड़ने से लाभ नहीं होगा, क्योंकि उसे `BQ-004` की `values` नियंत्रित करती है। |
| यह रजिस्टर टेम्पलेट से उतारा गया है: दो पंक्तियों का क्रमांक `3` एक ही है, और एक `要求内容` कोष्ठ में अब भी `待填` लिखा है। | `BQ-007` दोहराया गया `序号` दर्ज करता है (तुलना में खाली स्थान छोड़े जाते हैं, इसलिए `3` और ` 3 ` एक ही क्रमांक हैं) और यदि किसी पंक्ति में क्रमांक ही न हो तो पास होने के बजाय `skipped` बताता है। `BQ-008` `要求内容` में बचा प्लेसहोल्डर दर्ज करता है — `【`, `】`, `{{`, `}}`, `XXX`, `待填`, `待补充`, `TBD`, `示例` और उसकी `terms` सूची के शेष शब्द, जिसे आप छोटा कर सकते हैं। दोनों जाँचें शाब्दिक हैं: कोई भी यह नहीं आँकती कि आवश्यकता स्वयं सही है, और शब्दशः उतारी गई आवश्यकता में `XXX` हो तो वह भी दर्ज होती है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-bid-qual-check
dsh --profile <name> --dump-config | grep 'dsh-bid-qual-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/bid-qual-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-bid-qual-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-bid-qual-check contributors.
