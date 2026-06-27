from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from safety_video_harness.io import read_json


PROJECT_LAYOUT_VERSION: Final = 2


class LayoutKey(StrEnum):
    SOURCE_RAW = "source_raw"
    SOURCE_RENDERED = "source_rendered"
    SOURCE_REGISTRY = "source_registry"
    SOURCE_TOPICS = "source_topics"
    SOURCE_FACTS = "source_facts"
    REFS_CAST = "refs_cast"
    REFS_PPE = "refs_ppe"
    REFS_EQUIPMENT = "refs_equipment"
    REFS_CANDIDATES = "refs_candidates"
    REFS_APPROVED = "refs_approved"
    REFS_PERSON = "refs_person"
    REFS_WORK = "refs_work"
    REFS_SPACE = "refs_space"
    REFS_STYLE = "refs_style"
    REFS_CAMERA = "refs_camera"
    REFS_LIGHTING = "refs_lighting"
    REFS_ASSET_LOCK = "refs_asset_lock"
    STORY_SCENES = "story_scenes"
    STORY_VERSIONS = "story_versions"
    STORY_IMAGE_PROMPTS = "story_image_prompts"
    STORY_VIDEO_PROMPTS = "story_video_prompts"
    STORY_IMAGE_PROMPT_TEAM = "story_image_prompt_team"
    STORY_IMAGEGEN_JOBS = "story_imagegen_jobs"
    MEDIA_IMAGE_DRAFT = "media_image_draft"
    MEDIA_IMAGE_APPROVED = "media_image_approved"
    MEDIA_IMAGE_REJECTED = "media_image_rejected"
    MEDIA_VIDEO_CLIPS = "media_video_clips"
    MEDIA_VIDEO_SAMPLED_FRAMES = "media_video_sampled_frames"
    MEDIA_VIDEO_INSPECTION = "media_video_inspection"
    MEDIA_AUDIO = "media_audio"
    MEDIA_SUBTITLES = "media_subtitles"
    MEDIA_OUTPUT = "media_output"
    QA_ROOT = "qa_root"
    QA_APPROVALS = "qa_approvals"
    QA_STATE = "qa_state"
    QA_EVIDENCE = "qa_evidence"


CANONICAL_PROJECT_PATHS: Final[dict[LayoutKey, str]] = {
    LayoutKey.SOURCE_RAW: "input/sources/raw",
    LayoutKey.SOURCE_RENDERED: "input/sources/rendered",
    LayoutKey.SOURCE_REGISTRY: "input/sources.json",
    LayoutKey.SOURCE_TOPICS: "input/extracted_topics.json",
    LayoutKey.SOURCE_FACTS: "input/source_facts.json",
    LayoutKey.REFS_CAST: "refs/people",
    LayoutKey.REFS_PPE: "refs/ppe",
    LayoutKey.REFS_EQUIPMENT: "refs/equipment",
    LayoutKey.REFS_CANDIDATES: "refs/candidates",
    LayoutKey.REFS_APPROVED: "refs/approved",
    LayoutKey.REFS_PERSON: "refs/approved/people",
    LayoutKey.REFS_WORK: "refs/approved/work",
    LayoutKey.REFS_SPACE: "refs/approved/spaces",
    LayoutKey.REFS_STYLE: "refs/approved/style",
    LayoutKey.REFS_CAMERA: "refs/approved/camera",
    LayoutKey.REFS_LIGHTING: "refs/approved/lighting",
    LayoutKey.REFS_ASSET_LOCK: "refs/asset-lock",
    LayoutKey.STORY_SCENES: "story/scenes.json",
    LayoutKey.STORY_VERSIONS: "story/versions",
    LayoutKey.STORY_IMAGE_PROMPTS: "story/image_prompts.json",
    LayoutKey.STORY_VIDEO_PROMPTS: "story/video_prompts.json",
    LayoutKey.STORY_IMAGE_PROMPT_TEAM: "story/image_prompt_team_plan.json",
    LayoutKey.STORY_IMAGEGEN_JOBS: "story/imagegen_jobs.json",
    LayoutKey.MEDIA_IMAGE_DRAFT: "media/images/draft",
    LayoutKey.MEDIA_IMAGE_APPROVED: "media/images/approved",
    LayoutKey.MEDIA_IMAGE_REJECTED: "media/images/rejected",
    LayoutKey.MEDIA_VIDEO_CLIPS: "media/video/clips",
    LayoutKey.MEDIA_VIDEO_SAMPLED_FRAMES: "media/video/sampled_frames",
    LayoutKey.MEDIA_VIDEO_INSPECTION: "media/video/inspection",
    LayoutKey.MEDIA_AUDIO: "media/audio",
    LayoutKey.MEDIA_SUBTITLES: "media/subtitles",
    LayoutKey.MEDIA_OUTPUT: "media/output",
    LayoutKey.QA_ROOT: "qa",
    LayoutKey.QA_APPROVALS: "qa/approvals.json",
    LayoutKey.QA_STATE: "qa/state",
    LayoutKey.QA_EVIDENCE: "qa/evidence",
}

OLD_PROJECT_PATHS: Final[dict[LayoutKey, tuple[str, ...]]] = {
    LayoutKey.SOURCE_RAW: ("sources/raw",),
    LayoutKey.SOURCE_RENDERED: ("sources/rendered",),
    LayoutKey.SOURCE_REGISTRY: ("sources/sources.json",),
    LayoutKey.SOURCE_TOPICS: ("sources/extracted_topics.json",),
    LayoutKey.SOURCE_FACTS: ("sources/source_facts.json",),
    LayoutKey.REFS_CAST: ("model/cast",),
    LayoutKey.REFS_PPE: ("model/ppe",),
    LayoutKey.REFS_EQUIPMENT: ("product/equipment",),
    LayoutKey.REFS_CANDIDATES: ("ref/candidates",),
    LayoutKey.REFS_APPROVED: ("ref/approved",),
    LayoutKey.REFS_PERSON: ("ref/approved/person",),
    LayoutKey.REFS_WORK: ("ref/approved/work",),
    LayoutKey.REFS_SPACE: ("ref/approved/space",),
    LayoutKey.REFS_STYLE: ("ref/approved/style", "style"),
    LayoutKey.REFS_CAMERA: ("ref/approved/camera",),
    LayoutKey.REFS_LIGHTING: ("ref/approved/lighting",),
    LayoutKey.REFS_ASSET_LOCK: ("asset-lock",),
    LayoutKey.STORY_SCENES: ("storyboard/scenes.json",),
    LayoutKey.STORY_VERSIONS: ("storyboard/versions",),
    LayoutKey.STORY_IMAGE_PROMPTS: ("prompts/image_prompts.json",),
    LayoutKey.STORY_VIDEO_PROMPTS: ("prompts/video_prompts.json",),
    LayoutKey.STORY_IMAGE_PROMPT_TEAM: ("prompts/image_prompt_team_plan.json",),
    LayoutKey.STORY_IMAGEGEN_JOBS: ("prompts/imagegen_jobs.json",),
    LayoutKey.MEDIA_IMAGE_DRAFT: ("images/draft",),
    LayoutKey.MEDIA_IMAGE_APPROVED: ("images/approved",),
    LayoutKey.MEDIA_IMAGE_REJECTED: ("images/rejected",),
    LayoutKey.MEDIA_VIDEO_CLIPS: ("video/clips",),
    LayoutKey.MEDIA_VIDEO_SAMPLED_FRAMES: ("video/sampled_frames",),
    LayoutKey.MEDIA_VIDEO_INSPECTION: ("video/inspection",),
    LayoutKey.MEDIA_AUDIO: ("audio",),
    LayoutKey.MEDIA_SUBTITLES: ("subtitles",),
    LayoutKey.MEDIA_OUTPUT: ("output",),
    LayoutKey.QA_ROOT: ("qa",),
    LayoutKey.QA_APPROVALS: ("approvals.json",),
    LayoutKey.QA_STATE: (".harness",),
    LayoutKey.QA_EVIDENCE: ("evidence",),
}

OLD_PROJECT_DIRS: Final[tuple[str, ...]] = (
    "sources/raw",
    "sources/rendered",
    "model/cast",
    "model/ppe",
    "product/equipment",
    "ref/candidates",
    "ref/approved",
    "ref/approved/person",
    "ref/approved/work",
    "ref/approved/space",
    "ref/approved/style",
    "ref/approved/camera",
    "ref/approved/lighting",
    "style",
    "asset-lock",
    "storyboard/versions",
    "prompts",
    "images/draft",
    "images/approved",
    "images/rejected",
    "video/clips",
    "video/sampled_frames",
    "video/inspection",
    "audio",
    "subtitles",
    "output",
    "qa",
    "evidence",
    ".harness",
)

CANONICAL_PROJECT_DIRS: Final[tuple[str, ...]] = (
    "input/sources/raw",
    "input/sources/rendered",
    "refs/people",
    "refs/ppe",
    "refs/equipment",
    "refs/candidates",
    "refs/approved",
    "refs/approved/people",
    "refs/approved/work",
    "refs/approved/spaces",
    "refs/approved/style",
    "refs/approved/camera",
    "refs/approved/lighting",
    "refs/asset-lock",
    "story/versions",
    "media/images/draft",
    "media/images/approved",
    "media/images/rejected",
    "media/video/clips",
    "media/video/sampled_frames",
    "media/video/inspection",
    "media/audio",
    "media/subtitles",
    "media/output",
    "qa/state",
    "qa/evidence",
)


@dataclass(frozen=True, slots=True)
class ProjectLayout:
    project: Path
    version: int

    def write_path(self, key: LayoutKey) -> Path:
        return self.project / CANONICAL_PROJECT_PATHS[key]

    def read_path(self, key: LayoutKey) -> Path:
        canonical = self.write_path(key)
        if canonical.exists():
            return canonical
        for old_relative_path in OLD_PROJECT_PATHS[key]:
            old_path = self.project / old_relative_path
            if old_path.exists():
                return old_path
        return canonical


def layout_for_project(project: Path) -> ProjectLayout:
    return ProjectLayout(project=project, version=_detect_layout_version(project))


def _detect_layout_version(project: Path) -> int:
    config_path = project / "project_config.json"
    if not config_path.exists():
        return 1
    config = read_json(config_path)
    return PROJECT_LAYOUT_VERSION if config.get("project_layout_version") == PROJECT_LAYOUT_VERSION else 1
