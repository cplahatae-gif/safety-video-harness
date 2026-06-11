# Remicon Image Generation Run

Date: 2026-06-11

Project:
- `projects/remicon-collision-guide`

Source:
- `fixtures/sources/remicon-collision-guide.pptx`
- Rendered PPT images: `projects/remicon-collision-guide/sources/rendered/`

Generated assets:
- `projects/remicon-collision-guide/creative_brief.md`
- `projects/remicon-collision-guide/images/draft/sc01.png`
- `projects/remicon-collision-guide/images/draft/sc02.png`
- `projects/remicon-collision-guide/images/draft/sc03.png`
- `projects/remicon-collision-guide/images/draft/sc04.png`
- `projects/remicon-collision-guide/images/draft/sc05.png`
- `projects/remicon-collision-guide/images/draft/sc06.png`
- `projects/remicon-collision-guide/images/draft/sc07.png`
- `projects/remicon-collision-guide/images/draft/sc01_v001.png`
- `projects/remicon-collision-guide/images/draft/sc02_v001.png`
- `projects/remicon-collision-guide/images/draft/sc03_v001.png`
- `projects/remicon-collision-guide/images/draft/sc04_v001.png`
- `projects/remicon-collision-guide/images/draft/sc05_v001.png`
- `projects/remicon-collision-guide/images/draft/sc06_v001.png`
- `projects/remicon-collision-guide/images/draft/sc07_v001.png`
- `projects/remicon-collision-guide/images/draft/contact_sheet.png`

Storyboard basis:
- 30 seconds
- 6 clips at 5 seconds each
- 7 keyframes for sliding start/end frame chaining

Validation:
```text
uv run python scripts/validate_images.py --project projects/remicon-collision-guide
validated 6 image plan(s)
```

```text
uv run python scripts/validate_project.py projects/remicon-collision-guide
project valid
```

Notes:
- Images were generated with Codex built-in imagegen.
- Higgsfield/Seedance video generation was not run.
- Approved image promotion was not run; outputs remain in `images/draft` for user review.
