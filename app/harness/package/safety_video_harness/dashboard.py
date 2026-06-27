from __future__ import annotations

import html
from pathlib import Path

from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def build_storyboard_dashboard(project: Path) -> str:
    layout = layout_for_project(project)
    scenes = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    config = read_json(project / "project_config.json")
    prompts_path = layout.read_path(LayoutKey.STORY_IMAGE_PROMPTS)
    prompt_ids = _prompt_ids(prompts_path)
    output = project / "dashboard" / "storyboard-review.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_dashboard_html(config, scenes, prompt_ids), encoding="utf-8")
    write_json(
        project / "dashboard" / "storyboard-review.json",
        {
            "dashboard": str(output.relative_to(project)),
            "scene_count": len(list(scenes.get("scenes", []))),
            "prompt_count": len(prompt_ids),
        },
    )
    return f"storyboard dashboard written: {output}"


def _prompt_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    prompts = read_json(path)
    return {str(plan.get("scene_id")) for plan in list(prompts.get("plans", []))}


def _dashboard_html(config: dict, scenes: dict, prompt_ids: set[str]) -> str:
    rows = "\n".join(_scene_row(scene, prompt_ids) for scene in list(scenes.get("scenes", [])))
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Storyboard Review</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f7f9; color: #18202a; }}
    header {{ padding: 28px 32px; background: #17212f; color: white; }}
    main {{ padding: 24px 32px 40px; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 16px; }}
    .meta div, section {{ background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 14px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d9dee7; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e8ebf0; vertical-align: top; text-align: left; font-size: 14px; }}
    th {{ background: #edf1f6; font-weight: 700; }}
    .ok {{ color: #0b7a3b; font-weight: 700; }}
    .missing {{ color: #a33a00; font-weight: 700; }}
    .small {{ color: #5c6776; font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(str(config.get("project_name", "Storyboard Review")))}</h1>
    <div class="meta">
      <div>Topic<br><b>{html.escape(str(config.get("topic", "")))}</b></div>
      <div>Target<br><b>{html.escape(str(config.get("target_seconds", "")))} sec</b></div>
      <div>Style<br><b>{html.escape(str(config.get("style_guide_id", "")))}</b></div>
      <div>Gate<br><b>Storyboard review before image/video</b></div>
    </div>
  </header>
  <main>
    <table>
      <thead>
        <tr>
          <th>Scene</th>
          <th>Education Goal</th>
          <th>Visual Beat</th>
          <th>Subtitle</th>
          <th>Keyframes</th>
          <th>Sources</th>
          <th>Prompt</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </main>
</body>
</html>
"""


def _scene_row(scene: dict, prompt_ids: set[str]) -> str:
    scene_id = str(scene.get("id", ""))
    prompt_status = "ready" if scene_id in prompt_ids else "not generated"
    prompt_class = "ok" if scene_id in prompt_ids else "missing"
    citations = "<br>".join(
        html.escape(f"{item.get('source_id', '')} / {item.get('page_or_slide', '')}: {item.get('claim', '')}")
        for item in list(scene.get("source_citations", []))
    )
    return f"""<tr>
  <td><b>{html.escape(scene_id)}</b><br><span class="small">{html.escape(str(scene.get("duration_sec", "")))} sec</span></td>
  <td>{html.escape(str(scene.get("educational_goal_ko", "")))}</td>
  <td>{html.escape(str(scene.get("visual_action_ko", "")))}</td>
  <td>{html.escape(str(scene.get("subtitle_ko", scene.get("caption_ko", ""))))}</td>
  <td>{html.escape(str(scene.get("start_keyframe", "")))}<br>{html.escape(str(scene.get("end_keyframe", "")))}</td>
  <td>{citations}</td>
  <td><span class="{prompt_class}">{prompt_status}</span></td>
</tr>"""
