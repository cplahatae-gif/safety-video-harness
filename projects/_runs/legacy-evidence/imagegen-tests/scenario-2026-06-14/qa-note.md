# QA Note

Date: 2026-06-14

Artifacts:
- `storyboard.md`
- `images/sc01-hazard-context.png`
- `images/sc02-stop-confirm.png`
- `images/sc03-verify-safe-route.png`
- `images/sc04-controlled-safe-movement.png`
- `contact-sheet.png`

## Quick Review

Passes:
- The four frames follow a causal safety flow: hazard context -> stop signal -> route verification -> controlled safe movement.
- Gaze motivation is clearer than earlier attempts: signal worker and driver have visible targets.
- Generated text is avoided inside keyframes.
- The topic reads as vehicle-entry collision/contact prevention in a ready-mix plant.

Production blockers:
- Site prop continuity fails: the large orange convex mirror is absent in sc01 but appears in sc02-sc04.
- Road/lane continuity is unstable: sc01 uses a blue-toned vehicle lane plus a red/yellow hazard zone, while sc02-sc04 shift to a gray vehicle lane and omit the same red/yellow hazard-zone geometry.
- Hazard-zone continuity fails: the red hazard circle/arc shown in sc01 disappears in later scenes, so the viewer cannot track the same risk area.
- Camera continuity is only partially controlled: sc01 is a different wider angle; sc02-sc04 become nearly the same composition, which reduces the sense of intentional story progression.
- Vehicle movement is insufficient between sc03 and sc04: the BCT appears almost in the same position, so "controlled safe movement" is not visually distinct.
- Character identity is approximate, not locked. The signal worker and driver are similar enough for a test, but not production-grade without cast/model references.

Non-blocking issues:
- The style is still closer to semi-realistic industrial webtoon than strong Naver-webtoon-like cel illustration.

Next prompt improvements:
- Create a continuity bible before regeneration:
  - fixed site props: orange convex mirror must appear in every frame at the same right-side pole location, or be removed from every frame.
  - fixed lane colors: vehicle lane gray concrete, pedestrian lane desaturated green, hazard zone red/orange arc at the same crossing area.
  - fixed vehicle positions per scene: sc01 approach before stop line, sc02 stopped before line, sc03 stopped while route verified, sc04 nose advanced one truck length after confirmation.
  - fixed cast: one signal worker, one BCT driver, one ground worker only from sc03 onward.
- Add: "make sc04 visibly later than sc03; the BCT nose has advanced one truck length past the stop line while still clear of the pedestrian lane."
- Add stronger style lock: "less photorealistic texture, flatter cel shading, cleaner webtoon line art, simplified concrete texture."
- Use a model/cast reference pack before production generation.

Decision:
- Good enough only for imagegen integration and multi-image scenario testing.
- Not acceptable for production or Seedance keyframes.
- Regenerate from a fixed continuity bible rather than fixing one image at a time.
