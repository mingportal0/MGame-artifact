# F05 — Korean/English language selection: verified implementation

Status: implementation and isolated execution verification complete for this feature. This is not final visual approval, human usability validation, or integrated acceptance of the demo.

## Delivered behavior
- Explicit 한국어 / English selection before first play; no automatic confirmation from focus or Escape.
- Only the language code is persisted. Progress, purchases and currency reset on restart.
- Missing, empty, unsupported or corrupt settings show the bilingual chooser with an internal English safety default.
- Settings can change language without replacing the game model. Opening settings during battle pauses it. Closing settings does not resume; Resume is a separate action.
- Storage failure applies the choice for the session and persistently explains that the next launch may use an old choice or require selection again.
- Korean/English coverage includes HUD, shop names/descriptions and purchase states, enemy toggles, command/pause/settings messages, results and storage errors. Existing always-visible descriptions serve the role of item help; no new hover-tooltip subsystem was added.
- Next-battle settings and settings used in the current battle are displayed separately. Elite counts are labeled as spawned, and result rewards are identified as already credited.
- The combat/economy model is unchanged from the prior verified feature. The forthcoming dedicated-unlock/tree and formation work is not included.

## Actual verification
Environment: Unity 6000.6.7f1, Windows64, 1280×800 windowed, in the existing approved isolated project. The protected original Editor was not manipulated.

| Layer | Observed result |
|---|---|
| Font import and sample rasterization | exit 0; 40/40 sampled Korean characters, no missing glyphs |
| Final EditMode NUnit | 8/8, zero failures |
| Final PlayMode NUnit | 2/2, zero failures |
| Play internal checks | Existing live regression 37/37; language checks 26/26, not added to NUnit totals |
| Final Windows build | exit 0 and success log |
| First launch / saved Korean / saved English / corrupt setting / real second-process reload | Each player run 27/27, exit 0 |
| Real-time natural-income regression | 37/37, exit 0; separate from funded language-screen fixtures |
| Independently copied delivery and ZIP-extracted delivery | Each 27/27, exit 0 |
| Artifact integrity | 201-file manifests match across build, copied delivery, internal archive and extracted ZIP; ZIP CRC checked |
| Original protection | 75 protected files unchanged in this execution's before/after hashes |

The final language probe checks explicit selection, background-action rejection, same-frame input rejection, settings pause/state preservation, explicit resume, actual storage failure, persistence reload, fallback text, glyph coverage, forward Tab containment, and the final toggle's full viewport containment and activation via synthetic Submit.

33 actual final player screenshots were preserved internally. The UX reviewer examined the requested final Korean/English evidence, including long/locked/owned item descriptions, last toggle ON/OFF, single Fire spirit, battle settings guidance and persistent English storage error.

## Immutable build identifiers
- Managed gameplay DLL SHA256: e7eb8b1804d8d336f1f21060ab0518aec297e41452a56fb940bc5704de4d634f
- Delivery ZIP SHA256: a0896b517316248142823b827e93f08776ad2975fc6c1ebf935e691836aef247
- Source manifest SHA256: 879543c68e63477ee04c606898d2e23b5b3d3ada0ac0cea1293a668f9cd98728
- Full build manifest SHA256: d53881e27302a381c4a748938178f81c631e177fe971d7d2f7990bc01334ad53

No source, binary, font file, internal screenshot, private execution path, or internal approval conversation is published with this report.

## Review and remaining risks
See F05-ux-review-summary.md and F05-font-approval-summary.md in this folder.

The reviewer accepted the specified static-screen improvements, not unrestricted UX quality. Central spirit/enemy overlap remains an observed defect assigned to the existing formation work. Fixed ownership labels mitigate missing ownership information but do not solve overlap. Physical OS mouse/keyboard/wheel input, reverse Tab/key repeat/Alt-Tab boundaries, human reading speed/fatigue/fun, all resolutions/DPI, agreed performance and integrated acceptance remain unverified. UI Toolkit synthetic events are not physical-input evidence. Funded screen fixtures are not natural-economy evidence.

Earlier compilation/helper failures are preserved internally and corrected before final execution. Initial 15-check player results were not relabeled as the later 27-check build. No new paid asset, package, translation service or external runtime dependency was introduced. The shared README was not modified.
