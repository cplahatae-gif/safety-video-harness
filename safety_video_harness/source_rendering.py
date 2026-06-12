from __future__ import annotations

from pathlib import Path
from shutil import which
from zipfile import BadZipFile, ZipFile

from safety_video_harness.errors import HarnessError


def extract_rendered_assets(rendered_dir: Path, entry: dict, index: int, mode: str) -> tuple[list[Path], str, str]:
    source = Path(str(entry["path"]))
    if source.suffix.lower() == ".pptx":
        if mode == "slide_render":
            if which("soffice") is None:
                assets = _extract_pptx_media(rendered_dir, source, str(entry["source_id"]))
                return assets, "media_extract", "soffice missing; used PPTX media extraction fallback"
            raise HarnessError("slide_render via soffice is not implemented yet; use --mode media_extract")
        assets = _extract_pptx_media(rendered_dir, source, str(entry["source_id"]))
        warning = "invalid pptx; used placeholder rendered asset" if _is_placeholder_asset(assets) else ""
        return assets, mode, warning
    output = rendered_dir / f"{entry['source_id']}_source_{index:02d}.txt"
    output.write_text(f"dry-run rendered asset for {entry['path']}\n", encoding="utf-8")
    return [output], mode, ""


def _extract_pptx_media(rendered_dir: Path, source: Path, source_id: str) -> list[Path]:
    assets: list[Path] = []
    try:
        with ZipFile(source) as archive:
            names = sorted(name for name in archive.namelist() if name.startswith("ppt/media/"))
            for index, name in enumerate(names, start=1):
                suffix = Path(name).suffix.lower()
                if suffix not in [".png", ".jpg", ".jpeg"]:
                    continue
                output = rendered_dir / f"{source_id}_slide_{index:02d}{suffix}"
                output.write_bytes(archive.read(name))
                assets.append(output)
    except BadZipFile:
        output = rendered_dir / f"{source_id}_slide_01.txt"
        output.write_text(f"dry-run placeholder for invalid pptx fixture: {source}\n", encoding="utf-8")
        return [output]
    if not assets:
        raise HarnessError(f"no renderable media found in {source}")
    return assets


def _is_placeholder_asset(assets: list[Path]) -> bool:
    return len(assets) == 1 and assets[0].suffix.lower() == ".txt"
