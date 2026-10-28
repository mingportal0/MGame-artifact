# F05 — approved font inclusion and verified compatibility

The existing Noto Sans KR variable font was explicitly approved for the internal demo and approved isolated delivery, together with its copyright notice and complete SIL Open Font License 1.1. This summary does not publish the internal approval conversation or grant a new external distribution scope.

The installed font was included without modification or conversion. No replacement download, paid resource, package or external runtime service was added. Its embedded copyright notice is © 2014–2021 Adobe, with Reserved Font Name “Source”. The font's embedded version identifies a non-release variable build; that risk was documented before compatibility testing.

Verification:
- Original/bundled font SHA256 match: 018174e8cdd366aff67c8d366c7dc806a7babbe7f2819fc23b00d59f7b8353d0.
- Static cmap inspection found all 11,172 modern precomposed Hangul syllables. This alone was not treated as Unity-rendering proof.
- Unity 6000.6.7f1 imported the font and rasterized all 40 sampled Korean characters without a missing glyph.
- Actual Windows player Korean/English UI screenshots were then reviewed. The specified visible Korean UI showed no observed replacement boxes; this does not prove all glyphs, environments or resolutions.
- Copyright and the full license accompany the delivery, including readable root-level notices.

Official license reference: https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE

Font inclusion approval and successful sample rendering are not final visual, accessibility or human legibility approval. Thin strokes and crowded combat remain a user-experience risk; the final feature uses a minimum 14px body size, stronger action/token styling and explicit spirit ownership labels. No font binary is published with this document.
