from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from shutil import which
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from safety_video_harness.errors import HarnessError
from safety_video_harness.external_tools import run_tool


def extract_rendered_assets(rendered_dir: Path, entry: dict, index: int, mode: str) -> tuple[list[Path], str, str]:
    source = Path(str(entry["path"]))
    if source.suffix.lower() == ".pptx":
        if mode == "slide_render":
            if which("soffice") is None:
                assets = _extract_pptx_media(rendered_dir, source, str(entry["source_id"]))
                return assets, "media_extract", "soffice missing; used PPTX media extraction fallback"
            if which("pdftoppm") is None:
                assets = _extract_pptx_media(rendered_dir, source, str(entry["source_id"]))
                return assets, "media_extract", "pdftoppm missing; used PPTX media extraction fallback"
            return _render_pptx_slides(rendered_dir, source, str(entry["source_id"])), "slide_render", ""
        assets = _extract_pptx_media(rendered_dir, source, str(entry["source_id"]))
        warning = "invalid pptx; used placeholder rendered asset" if _is_placeholder_asset(assets) else ""
        return assets, mode, warning
    output = rendered_dir / f"{entry['source_id']}_source_{index:02d}.txt"
    output.write_text(f"dry-run rendered asset for {entry['path']}\n", encoding="utf-8")
    return [output], mode, ""


def extract_pptx_text_assets(rendered_dir: Path, entry: dict) -> tuple[list[Path], str]:
    source = Path(str(entry["path"]))
    if source.suffix.lower() != ".pptx":
        return [], ""
    try:
        return _extract_pptx_text(rendered_dir, source, str(entry["source_id"])), ""
    except BadZipFile:
        output = rendered_dir / f"{entry['source_id']}_text_01.txt"
        output.write_text(f"invalid pptx text extraction placeholder: {source}\n", encoding="utf-8")
        return [output], "invalid pptx; used placeholder extracted text"


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


def _render_pptx_slides(rendered_dir: Path, source: Path, source_id: str) -> list[Path]:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        run_tool(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_dir),
                str(source),
            ],
            120,
            "PPTX slide_render failed during PDF conversion",
        )
        pdfs = sorted(tmp_dir.glob("*.pdf"))
        if not pdfs:
            raise HarnessError("PPTX slide_render failed: no PDF produced by soffice")
        prefix = tmp_dir / f"{source_id}_slide"
        run_tool(
            ["pdftoppm", "-png", "-r", "160", str(pdfs[0]), str(prefix)],
            120,
            "PPTX slide_render failed during PNG conversion",
        )
        rendered = sorted(tmp_dir.glob(f"{source_id}_slide-*.png"))
        if not rendered:
            raise HarnessError("PPTX slide_render failed: no PNG slides produced")
        outputs: list[Path] = []
        for index, image in enumerate(rendered, start=1):
            output = rendered_dir / f"{source_id}_rendered_slide_{index:02d}.png"
            copyfile(image, output)
            outputs.append(output)
        return outputs


def _extract_pptx_text(rendered_dir: Path, source: Path, source_id: str) -> list[Path]:
    assets: list[Path] = []
    with ZipFile(source) as archive:
        slide_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
        for index, name in enumerate(slide_names, start=1):
            text = _slide_text(archive.read(name))
            if not text:
                continue
            output = rendered_dir / f"{source_id}_text_{index:02d}.txt"
            output.write_text(text + "\n", encoding="utf-8")
            assets.append(output)
    return assets


def _slide_text(payload: bytes) -> str:
    root = ElementTree.fromstring(payload)
    texts = [
        node.text.strip()
        for node in root.iter()
        if node.tag.endswith("}t") and node.text and node.text.strip()
    ]
    return "\n".join(texts)


def _is_placeholder_asset(assets: list[Path]) -> bool:
    return len(assets) == 1 and assets[0].suffix.lower() == ".txt"
