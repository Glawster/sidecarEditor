from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from src.outputResolver import OutputResolver


def _touch(path: Path, *, mtime: float | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake")  # content doesn't matter
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def test_resolveOutput_returns_none_when_output_root_not_set(tmp_path: Path):
    r = OutputResolver(outputRoot=None)
    out = r.resolveOutput(str(tmp_path / "in.png"), inputRoot=str(tmp_path))
    assert out is None


def test_resolveOutput_returns_none_when_output_root_invalid(tmp_path: Path):
    r = OutputResolver(outputRoot=str(tmp_path / "does-not-exist"))
    out = r.resolveOutput(str(tmp_path / "in.png"), inputRoot=str(tmp_path))
    assert out is None


def test_resolveOutput_prefers_direct_filename_match(tmp_path: Path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()

    original = input_root / "img.png"
    original.write_bytes(b"orig")

    direct = output_root / "img.png"
    _touch(direct)

    r = OutputResolver(str(output_root))
    assert r.resolveOutput(str(original), inputRoot=str(input_root)) == str(direct)


def test_resolveOutput_stem_match_avoids_substring_collisions(tmp_path: Path):
    """
    Ensure 'clothed-15' does NOT match a file whose stem contains 'clothed-152'
    """
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()

    original = input_root / "clothed-15.png"
    original.write_bytes(b"orig")

    bad = output_root / "fixed_clothed-152_00001_.png"
    _touch(bad)

    r = OutputResolver(str(output_root))
    assert r.resolveOutput(str(original), inputRoot=str(input_root)) is None


def test_resolveOutput_when_multiple_candidates_picks_newest_mtime(tmp_path: Path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()

    original = input_root / "img.png"
    original.write_bytes(b"orig")

    older = output_root / "prefix_img_00001_.png"
    newer = output_root / "prefix_img_00002_.png"

    now = time.time()
    _touch(older, mtime=now - 10)
    _touch(newer, mtime=now)

    r = OutputResolver(str(output_root))
    assert r.resolveOutput(str(original), inputRoot=str(input_root)) == str(newer)