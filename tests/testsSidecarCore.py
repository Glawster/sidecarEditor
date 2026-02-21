from __future__ import annotations

from pathlib import Path

from src.sidecarCore import SidecarData, scanImages


def test_sidecarData_fromDict_handles_none():
    s = SidecarData.fromDict("/tmp/x.png", None)
    assert s.imagePath == "/tmp/x.png"
    assert s.data == {}


def test_sidecarData_roundtrip_dict():
    d = {"positive": {"subject": {"prompt": "abc"}}}
    s = SidecarData.fromDict("/tmp/x.png", d)
    assert s.toDict() == d


def test_scanImages_returns_sorted_images_and_skips_prompt_json(tmp_path: Path):
    # create images
    (tmp_path / "b.png").write_bytes(b"x")
    (tmp_path / "a.jpg").write_bytes(b"x")

    # should be skipped
    (tmp_path / "c.png.prompt.json").write_text("{}", encoding="utf-8")

    out = scanImages(str(tmp_path))

    # absolute paths, sorted
    assert out == sorted(out)
    assert str((tmp_path / "a.jpg").absolute()) in out
    assert str((tmp_path / "b.png").absolute()) in out
    assert not any(p.endswith(".prompt.json") for p in out)