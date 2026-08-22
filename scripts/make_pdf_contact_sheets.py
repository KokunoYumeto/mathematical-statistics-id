#!/usr/bin/env python3
"""Create compact contact sheets from task-local Poppler page renders."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("page_dir", type=Path)
    parser.add_argument("--per-sheet", type=int, default=20)
    args = parser.parse_args()
    pages = sorted(args.page_dir.glob("page-*.png"))
    if not pages:
        raise RuntimeError("no Poppler page images found")
    columns = 4
    rows = math.ceil(args.per_sheet / columns)
    thumb_width, thumb_height = 220, 311
    gap, label_height = 12, 22
    sheet_width = gap + columns * (thumb_width + gap)
    sheet_height = gap + rows * (thumb_height + label_height + gap)
    font = ImageFont.load_default(size=16)
    output_dir = args.page_dir / "contact-sheets"
    output_dir.mkdir()
    for sheet_index, start in enumerate(range(0, len(pages), args.per_sheet), start=1):
        sheet = Image.new("RGB", (sheet_width, sheet_height), "#d8dde2")
        draw = ImageDraw.Draw(sheet)
        for offset, page_path in enumerate(pages[start : start + args.per_sheet]):
            row, column = divmod(offset, columns)
            x = gap + column * (thumb_width + gap)
            y = gap + row * (thumb_height + label_height + gap)
            with Image.open(page_path) as source:
                page = source.convert("RGB")
                page.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                px = x + (thumb_width - page.width) // 2
                py = y + (thumb_height - page.height) // 2
                sheet.paste(page, (px, py))
            number = start + offset + 1
            draw.text((x, y + thumb_height + 2), f"PDF {number}", fill="#102536", font=font)
        destination = output_dir / f"contact-{sheet_index:02d}.png"
        sheet.save(destination, optimize=True)
    print(f"{len(pages)} pages -> {sheet_index} contact sheets")


if __name__ == "__main__":
    main()
