# F05 — independent UX review outcome summary

This implementation-owner summary reports actual independent UX feedback, not a replacement or fabricated reviewer approval. The full review records and screenshots remain internal.

## Review sequence and adopted changes
A pre-implementation copy/flow review was followed by an actual Korean/English player-screen review and a second review of the revised evidence.

Adopted copy corrections include:
- Enemy settings apply “from the next battle”, not “only in the next battle”. Ownership persists and changing the setting is free, not the purchase itself.
- Fire splash affects one other nearby enemy for 50% of Fire damage.
- Command radius is not attack range; Ice shatter does not require the separate slow upgrade.
- Elite probability applies when enabled; zero elites and no guaranteed extra reward remain explicit.
- Results distinguish spawned elites, settings used this battle, next-battle settings and already credited rewards.

Adopted flow/display changes include:
- Explicit bilingual first choice with language self-names; focus does not confirm a language.
- Bilingual settings entry, a current-language checkmark, and separate Close and Resume actions.
- Persistent storage-failure guidance explaining session application and possible next-launch outcomes.
- Minimum 14px body text, stronger action/token styling, fixed F/I/L ownership counts, variable-height item descriptions and complete last-toggle visibility evidence.

## Actual final static-screen acceptance
The reviewer inspected the requested 22 final 1280×800 PNGs and compared the earlier Korean/English battle captures. The specified improvements were accepted within that static-screen scope: single Fire identification, ownership information, complete U12 ON/OFF button display, long U07/lock/owned/purchasable/insufficient-currency text, battle-settings resume guidance, and English error both inside settings and after closing it.

The reviewer also checked the existing execution reports: early player 15/15 and revised player 27/27 are different versions. Revised EditMode 8/8, PlayMode 2/2 and build exit 0 were read from evidence, not rerun by the reviewer. Forward synthetic Tab and programmatic scroll/Submit evidence are not physical OS-input tests. Full viewport containment is stronger than partial overlap, but neither is human usability observation.

## Remaining findings
- Central Fire and enemy tokens still overlap. This is an observed unresolved display defect, tracked in the existing formation work, not solved by translation or ownership labels.
- Bold styling does not guarantee sufficient real-world stroke weight or fast combat reading. Dynamic readability, vision/color differences and fatigue need human testing.
- Dense shop guidance and the modest visual priority of storage errors remain non-blocking improvement recommendations.
- All resolutions/DPI, physical wheel/keyboard/Alt-Tab behavior, first-user comprehension, fun/economy and final visual approval remain outside this static review's acceptance.

The implementation owner may close the language feature's verified scope while preserving these explicit downstream risks. Neither this summary nor feature completion passes integrated demo acceptance.
