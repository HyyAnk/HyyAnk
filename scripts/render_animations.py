"""Render GitHub-safe animated profile assets without OS input automation.

The renderer creates GIFs because GitHub does not animate SVG files in rendered
repository views. Source SVG art direction remains in assets/ for editing.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.theme import Theme


console = Console(
    theme=Theme(
        {
            "time": "dim",
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "bold red",
            "step": "bold blue",
            "profile": "bright_cyan",
            "worker": "dim",
            "debug": "dim",
        }
    )
)

PROFILE_COLORS = [
    "cyan",
    "green",
    "yellow",
    "magenta",
    "blue",
    "bright_cyan",
    "bright_green",
    "bright_yellow",
    "bright_magenta",
    "bright_blue",
]
PROFILE_COLOR_CACHE: dict[str, str] = {}


def profile_color(profile_id: str) -> str:
    if profile_id not in PROFILE_COLOR_CACHE:
        index = int(hashlib.md5(profile_id.encode()).hexdigest(), 16) % len(PROFILE_COLORS)
        PROFILE_COLOR_CACHE[profile_id] = PROFILE_COLORS[index]
    return PROFILE_COLOR_CACHE[profile_id]


def log(
    level: str,
    message: str,
    *,
    profile_id: str = "HyyAnk",
    worker_id: str = "renderer-1",
    step: str = "render",
    style: str = "info",
) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(
        f"[time]{timestamp}[/time] [{style}][{level}][/{style}] "
        f"[worker][T:{worker_id}][/worker] "
        f"[{profile_color(profile_id)}][P:{profile_id}][/{profile_color(profile_id)}] "
        f"[step][STEP:{step}][/step] {message}"
    )


def font_path(*names: str) -> str:
    candidates = [Path("C:/Windows/Fonts") / name for name in names]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "arial.ttf"


FONT_DISPLAY = font_path("arialbd.ttf", "segoeuib.ttf", "arial.ttf")
FONT_SANS = font_path("arial.ttf", "segoeui.ttf")
FONT_MONO = font_path("consola.ttf", "cour.ttf")

BG = (11, 14, 14)
PAPER = (241, 241, 233)
MUTED = (215, 219, 212)
LIME = (199, 255, 26)
COBALT = (47, 100, 214)
GRID = (42, 49, 46)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, spacing: int = 92) -> None:
    for y in range(spacing, height, spacing):
        draw.line((0, y, width, y), fill=GRID, width=1)
    for x in range(spacing, width, spacing):
        draw.line((x, 0, x, height), fill=GRID, width=1)


def render_hero(frame: int, total: int, width: int = 1200, height: int = 480) -> Image.Image:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height)
    display = font(FONT_DISPLAY, 174)
    small = font(FONT_SANS, 13)
    mono = font(FONT_MONO, 11)
    center_x, center_y = 435, 275

    draw.text((42, 31), "HYYANK / DESIGN + BUILD", fill=MUTED, font=small, spacing=4)
    draw.line((40, 54, 510, 54), fill=COBALT, width=2)

    glitch_window = frame in {38, 39, 40}
    lime_offset = (-7, 2) if glitch_window else (0, 0)
    blue_offset = (7, -2) if glitch_window else (0, 0)
    kwargs = {"anchor": "mm", "stroke_width": 2}
    draw.text((center_x + blue_offset[0], center_y + blue_offset[1]), "HyyAnk", fill=BG, stroke_fill=COBALT, font=display, **kwargs)
    draw.text((center_x + lime_offset[0], center_y + lime_offset[1]), "HyyAnk", fill=BG, stroke_fill=LIME, font=display, **kwargs)
    draw.text((center_x, center_y), "HyyAnk", fill=PAPER, font=display, **kwargs)

    progress = min(1.0, frame / 19)
    line_end = 850 + int(215 * progress)
    draw.line((42, 352, line_end, 352), fill=LIME, width=3)
    draw.line((42, 366, 690, 366), fill=COBALT, width=2)

    orbit_x, orbit_y = 1000, 248
    draw.ellipse((orbit_x - 105, orbit_y - 105, orbit_x + 105, orbit_y + 105), outline=LIME, width=2)
    draw.ellipse((orbit_x - 76, orbit_y - 76, orbit_x + 76, orbit_y + 76), outline=(90, 120, 70), width=1)
    angle = (frame / total) * math.tau
    dot_x = orbit_x + math.cos(angle) * 105
    dot_y = orbit_y + math.sin(angle) * 105
    draw.ellipse((dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5), fill=LIME)
    draw.line((orbit_x - 126, orbit_y, orbit_x + 126, orbit_y), fill=(90, 96, 90), width=1)
    draw.line((orbit_x, orbit_y - 126, orbit_x, orbit_y + 126), fill=(90, 96, 90), width=1)
    draw.ellipse((orbit_x - 4, orbit_y - 4, orbit_x + 4, orbit_y + 4), fill=LIME)

    scan_y = int(((frame * 15) % (height + 36)) - 18)
    draw.rectangle((0, scan_y, width, scan_y + 2), fill=(90, 104, 93))
    draw.text((895, 421), "KINETIC IDENTITY", fill=MUTED, font=mono)
    draw.text((42, 422), "PRODUCT / VISUAL / MOTION / CODE", fill=MUTED, font=mono)
    return image


def cubic_point(t: float) -> tuple[float, float]:
    points = [(100, 154), (245, 38), (360, 38), (470, 154), (570, 270), (700, 270), (800, 154), (930, 38), (1100, 154)]
    segment = min(1, int(t * 2))
    local = (t * 2) - segment
    if segment == 0:
        p0, p1, p2, p3 = points[0], points[1], points[2], points[3]
    else:
        p0, p1, p2, p3 = points[4], points[5], points[6], points[7]
    inv = 1 - local
    x = inv**3 * p0[0] + 3 * inv**2 * local * p1[0] + 3 * inv * local**2 * p2[0] + local**3 * p3[0]
    y = inv**3 * p0[1] + 3 * inv**2 * local * p1[1] + 3 * inv * local**2 * p2[1] + local**3 * p3[1]
    return x, y


def render_process(frame: int, total: int, width: int = 1200, height: int = 266) -> Image.Image:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height, spacing=86)
    labels = [(100, 154, "FRAME"), (430, 116, "EXPLORE"), (760, 192, "PROTOTYPE"), (1100, 154, "SHIP")]
    path_points = [cubic_point(i / 80) for i in range(81)]
    draw.line(path_points, fill=(100, 108, 102), width=2)
    draw.line(path_points[::2], fill=BG, width=1)
    for index, (x, y, label) in enumerate(labels):
        pulse = 1 + 0.25 * math.sin((frame / total) * math.tau * 2 + index)
        radius = int(25 * pulse)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=LIME, width=2)
        draw.rectangle((x - 7, y - 7, x + 7, y + 7), fill=LIME)
        draw.text((x - len(label) * 5.2, y + 44), label, fill=PAPER, font=font(FONT_DISPLAY, 16))
    runner_x, runner_y = cubic_point((frame / total) % 1)
    draw.ellipse((runner_x - 14, runner_y - 14, runner_x + 14, runner_y + 14), fill=COBALT)
    draw.ellipse((runner_x - 5, runner_y - 5, runner_x + 5, runner_y + 5), fill=PAPER)
    return image


def save_gif(frames: list[Image.Image], path: Path, duration: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    quantized = [frame.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for frame in frames]
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def render_asset(name: str, count: int, renderer, output: Path, progress: Progress) -> None:
    task_id = progress.add_task(name, total=count)
    frames: list[Image.Image] = []
    for frame in range(count):
        frames.append(renderer(frame, count))
        progress.advance(task_id)
    save_gif(frames, output, duration=100)
    log("OK", f"Rendered {output.name} ({output.stat().st_size:,} bytes)", step=name, style="success")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("assets"))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()

    log(
        "INFO",
        "Starting animation render | config=1200px canvas, 48 frames, 10fps | profiles=1 | mode=local-render | concurrency=1 | automation=Pillow-code-renderer-no-OS-input",
        step="startup",
    )
    if args.debug:
        log("DEBUG", f"Output directory: {args.output_dir.resolve()}", step="startup", style="debug")

    try:
        with Progress(
            TextColumn("[step]{task.description}[/step]"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            render_asset("hero-wordmark", 48, render_hero, args.output_dir / "hyyank-hero.gif", progress)
            render_asset("design-process", 48, render_process, args.output_dir / "design-process.gif", progress)
    except Exception as exc:
        log(
            "ERROR",
            f"Render failed: {exc}. Suggested next action: verify Pillow and font files, then rerun with --debug.",
            step="render",
            style="error",
        )
        return 1

    elapsed = time.perf_counter() - started
    log(
        "DONE",
        f"Final summary | total=2 success=2 failed=0 skipped=0 retries=0 elapsed={elapsed:.2f}s",
        step="summary",
        style="success",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
