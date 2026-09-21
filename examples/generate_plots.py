#!/usr/bin/env python3
"""Regenerate example PNGs into this directory."""

from __future__ import annotations

from pathlib import Path

from twistdiff.cli import main

ROOT = Path(__file__).resolve().parent


def main_plots() -> None:
    main(["oscillator", "--plot", str(ROOT / "oscillator.png")])
    main(["cruise", "--plot", str(ROOT / "cruise.png")])


if __name__ == "__main__":
    main_plots()
