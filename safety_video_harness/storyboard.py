from __future__ import annotations

from math import ceil
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json


IMAGE_DENSITY_FACTORS = {"normal": 1, "high": 2, "very_high": 4}


def plan_storyboard(project: Path, duration: int, image_density: str = "normal") -> str:
    config = read_json(project / "project_config.json")
    _require_topic_selection(project, config)
    if image_density not in IMAGE_DENSITY_FACTORS:
        raise HarnessError("image-density must be one of: normal, high, very_high")
    seconds_per_clip = int(config.get("seconds_per_clip", 5))
    clip_count = max(1, ceil(duration / seconds_per_clip))
    story_beats = clip_count * IMAGE_DENSITY_FACTORS[image_density]
    planned_interval = duration / story_beats
    facts = _facts(project)
    citations = _citations_from_facts(facts)
    scenes = [
        _scene(index, max(1, round(planned_interval)), citations, _scene_plan(index, facts))
        for index in range(1, story_beats + 1)
    ]
    config["target_duration_sec"] = duration
    config["target_seconds"] = duration
    config["image_density"] = image_density
    write_json(project / "project_config.json", config)
    payload = {
        "schema_version": "2.1",
        "target_seconds": duration,
        "target_duration_sec": duration,
        "seconds_per_clip": seconds_per_clip,
        "image_density": image_density,
        "density_factor": IMAGE_DENSITY_FACTORS[image_density],
        "chain_policy": config.get("chain_policy", "hybrid"),
        "clip_count": clip_count,
        "story_beats": story_beats,
        "keyframe_count": story_beats + 1,
        "planned_anchor_interval_sec": planned_interval,
        "scenes": scenes,
    }
    write_json(project / "storyboard" / "scenes.json", payload)
    return f"planned {story_beats} story beat(s)"


def _require_topic_selection(project: Path, config: dict) -> None:
    topics_path = project / "sources" / "extracted_topics.json"
    if not topics_path.exists():
        return
    topics = list(read_json(topics_path).get("topics", []))
    if topics and not str(config.get("selected_topic_id", "")):
        raise HarnessError("topic must be selected before storyboard generation")


def _facts(project: Path) -> list[dict]:
    facts_path = project / "sources" / "source_facts.json"
    if not facts_path.exists():
        return []
    return list(read_json(facts_path).get("facts", []))


def _citations_from_facts(facts: list[dict]) -> list[dict]:
    if not facts:
        return [{"source_id": "user-note", "page_or_slide": 1, "claim": "사용자 승인 안전 주제"}]
    first = facts[0]
    return [
        {
            "source_id": first["source_id"],
            "page_or_slide": first.get("page_or_slide", 1),
            "claim": first["claim"],
        }
    ]


def _scene(index: int, duration: int, citations: list[dict], scene_plan: dict) -> dict:
    scene_id = f"sc{index:02d}"
    next_id = f"sc{index + 1:02d}"
    return {
        "id": scene_id,
        "duration_sec": duration,
        "educational_goal_ko": scene_plan["goal"],
        "source_citations": [scene_plan.get("citation", citations[0])],
        "visual_action_ko": scene_plan["visual"],
        "caption_ko": scene_plan["caption"],
        "subtitle_ko": scene_plan["subtitle"],
        "overlay_text_ko": scene_plan["caption"],
        "image_prompt_en": scene_plan["image_prompt"],
        "motion_prompt_en": scene_plan["motion_prompt"],
        "start_keyframe": f"images/approved/{scene_id}.png",
        "end_keyframe": f"images/approved/{next_id}.png",
        "clip_path": f"video/clips/{scene_id}_{next_id}.mp4",
        "continuity_constraints": {
            "character_ids": ["worker-001"],
            "equipment_ids": ["equipment-001"],
            "ppe_requirements": ["hard hat", "safety vest"],
            "background_id": "site-001",
        },
        "approval_state": "draft",
        "asset_version": 1,
    }


def _scene_plan(index: int, facts: list[dict]) -> dict:
    if _has_keyword(facts, "레미콘"):
        return _remicon_scene_plan(index, facts)
    return {
        "goal": "위험요인을 인지하고 올바른 행동을 선택한다.",
        "visual": "작업자가 위험구역을 확인하고 안전한 위치로 이동한다.",
        "caption": "위험구역 확인",
        "subtitle": "위험구역을 먼저 확인하세요.",
        "image_prompt": (
            "Industrial safety training animation, worker wearing hard hat and vest, "
            "clear equipment spacing, wide educational camera, no text, no injury."
        ),
        "motion_prompt": (
            "Start from the approved keyframe, slow camera push, worker checks hazard zone, "
            "keep PPE and equipment unchanged, no impact."
        ),
        "citation": _citation_for(facts, 0),
    }


def _remicon_scene_plan(index: int, facts: list[dict]) -> dict:
    plans = [
        {
            "goal": "대형차량 진입·하역 작업의 충돌 위험을 인지한다.",
            "visual": "레미콘 사업장 입구에서 BCT와 덤프트럭 동선이 분리되어 표시된다.",
            "action_en": "separated traffic lanes for a BCT bulk cement trailer and a dump truck at a ready-mix concrete plant entrance",
            "caption": "대형차량 동선 확인",
            "subtitle": "차량 동선을 먼저 확인하세요.",
            "keywords": ["레미콘", "대형차량"],
        },
        {
            "goal": "사각지대 보행자 충돌 위험을 확인한다.",
            "visual": "덤프트럭 후진 경로 옆 사각지대에 보행자 접근 금지 표시가 보인다.",
            "action_en": "a marked blind spot beside a reversing dump truck route with pedestrians kept outside the hazard zone",
            "caption": "사각지대 접근 금지",
            "subtitle": "사각지대 접근을 금지하세요.",
            "keywords": ["사각지대", "후진"],
        },
        {
            "goal": "신호수 배치와 운전원 소통의 필요성을 이해한다.",
            "visual": "신호수가 신호봉과 무전기로 BCT 운전원에게 정지 신호를 보낸다.",
            "action_en": "a signal person using a baton and radio to communicate a stop signal to the BCT driver",
            "caption": "신호수 배치",
            "subtitle": "신호수와 계속 소통하세요.",
            "keywords": ["신호수", "무전기"],
        },
        {
            "goal": "후방카메라와 후방 확인의 중요성을 이해한다.",
            "visual": "운전원이 후방카메라와 거울을 확인한 뒤 천천히 후진을 준비한다.",
            "action_en": "a driver checking the rear camera and mirrors before slowly reversing the heavy vehicle",
            "caption": "후방 확인",
            "subtitle": "후방을 확인한 뒤 후진하세요.",
            "keywords": ["후방카메라", "후진"],
        },
        {
            "goal": "지정 구역 외 임의 작업과 통로 침범을 금지한다.",
            "visual": "작업자가 지정 구역 밖 차량 통로로 들어가려다 관리감독자의 안내로 멈춘다.",
            "action_en": "a worker stopping before entering a vehicle passage outside the designated work zone while a supervisor redirects them",
            "caption": "지정구역 준수",
            "subtitle": "지정구역 밖 작업은 금지입니다.",
            "keywords": ["지정구역", "끼임"],
        },
        {
            "goal": "속도 제한과 보행 중 스마트폰 금지를 준수한다.",
            "visual": "현장 표지판에 제한속도 10~20km와 스마트폰 사용 금지가 표시된다.",
            "action_en": "site safety signs showing a 10 to 20 km speed limit and no smartphone use while walking",
            "caption": "속도와 보행 수칙",
            "subtitle": "속도와 보행 수칙을 지키세요.",
            "keywords": ["제한속도", "스마트폰"],
        },
    ]
    selected = plans[(index - 1) % len(plans)]
    citation = _citation_matching(facts, list(selected["keywords"]))
    return {
        "goal": selected["goal"],
        "visual": selected["visual"],
        "caption": selected["caption"],
        "subtitle": selected["subtitle"],
        "image_prompt": _remicon_image_prompt(str(selected["action_en"])),
        "motion_prompt": _remicon_motion_prompt(str(selected["action_en"])),
        "citation": citation,
    }


def _remicon_image_prompt(visual: str) -> str:
    return (
        "Korean industrial safety training animation style, ready-mix concrete plant, "
        "BCT bulk cement trailer and dump truck, signal person with orange vest, hard hat, "
        f"scene action: {visual}, clear blind spot zone, safe pedestrian route, no text, "
        "no injury, no impact frame."
    )


def _remicon_motion_prompt(visual: str) -> str:
    return (
        "Use start and end keyframes as a continuous safety training shot, slow camera movement, "
        f"show this action: {visual}, keep BCT, dump truck, PPE, signal person, and plant layout "
        "consistent, avoid collision or injury depiction."
    )


def _has_keyword(facts: list[dict], keyword: str) -> bool:
    return any(keyword in str(fact.get("claim", "")) for fact in facts)


def _citation_matching(facts: list[dict], keywords: list[str]) -> dict:
    for fact in facts:
        claim = str(fact.get("claim", ""))
        if any(keyword in claim for keyword in keywords):
            return _citation_for_fact(fact)
    return _citation_for(facts, 0)


def _citation_for(facts: list[dict], index: int) -> dict:
    if not facts:
        return {"source_id": "user-note", "page_or_slide": 1, "claim": "사용자 승인 안전 주제"}
    selected = facts[min(index, len(facts) - 1)]
    return _citation_for_fact(selected)


def _citation_for_fact(fact: dict) -> dict:
    return {
        "source_id": fact["source_id"],
        "page_or_slide": fact.get("page_or_slide", 1),
        "claim": fact["claim"],
    }
