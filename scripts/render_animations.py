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

BG = (8, 10, 13)
PAPER = (242, 245, 246)
MUTED = (197, 208, 214)
RED = (240, 46, 77)
CYAN = (0, 217, 245)
GRID = (35, 43, 47)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, spacing: int = 92) -> None:
    for y in range(spacing, height, spacing):
        draw.line((0, y, width, y), fill=GRID, width=1)
    for x in range(spacing, width, spacing):
        draw.line((x, 0, x, height), fill=GRID, width=1)


def mangekyou_blade_points(
    center_x: float,
    center_y: float,
    radius: float,
    rotation: float,
) -> list[tuple[float, float]]:
    """Build one curved Itachi-style Mangekyou blade as a polar polygon."""
    start_radius = radius * 0.12
    end_radius = radius * 0.88
    steps = 28
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for index in range(steps + 1):
        progress = index / steps
        current_radius = start_radius + (end_radius - start_radius) * progress
        sweep = progress * 1.02
        half_width = 0.42 - (0.13 * progress)
        outer_angle = rotation + sweep + half_width
        inner_angle = rotation + sweep - half_width
        outer.append(
            (
                center_x + math.cos(outer_angle) * current_radius,
                center_y + math.sin(outer_angle) * current_radius,
            )
        )
        inner.append(
            (
                center_x + math.cos(inner_angle) * current_radius,
                center_y + math.sin(inner_angle) * current_radius,
            )
        )
    return outer + list(reversed(inner))


def draw_mangekyou(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    radius: int,
    rotation: float,
    pulse: float,
) -> None:
    """Draw a brand-colored three-blade Mangekyou Sharingan motif."""
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=(17, 22, 19),
        outline=RED,
        width=3,
    )
    inner_radius = radius - 13
    draw.ellipse(
        (
            center_x - inner_radius,
            center_y - inner_radius,
            center_x + inner_radius,
            center_y + inner_radius,
        ),
        outline=(63, 85, 36),
        width=1,
    )

    for blade_index in range(3):
        blade_rotation = rotation + (blade_index * math.tau / 3)
        shadow = mangekyou_blade_points(center_x, center_y, radius, blade_rotation + 0.035)
        blade = mangekyou_blade_points(center_x, center_y, radius, blade_rotation)
        draw.polygon(shadow, fill=CYAN)
        draw.polygon(blade, fill=RED)

    pupil_radius = int(15 + pulse * 2)
    draw.ellipse(
        (
            center_x - pupil_radius,
            center_y - pupil_radius,
            center_x + pupil_radius,
            center_y + pupil_radius,
        ),
        fill=BG,
        outline=PAPER,
        width=2,
    )
    draw.ellipse(
        (center_x - 5, center_y - 5, center_x + 5, center_y + 5),
        fill=RED,
    )


def render_hero(frame: int, total: int, width: int = 1200, height: int = 480) -> Image.Image:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height)
    display = font(FONT_DISPLAY, 174)
    small = font(FONT_SANS, 13)
    mono = font(FONT_MONO, 11)
    center_x, center_y = 435, 275

    draw.text((42, 31), "HYYANK / DESIGN + BUILD", fill=MUTED, font=small, spacing=4)
    draw.line((40, 54, 510, 54), fill=CYAN, width=2)

    glitch_window = frame in {38, 39, 40}
    red_offset = (-7, 2) if glitch_window else (0, 0)
    cyan_offset = (7, -2) if glitch_window else (0, 0)
    kwargs = {"anchor": "mm", "stroke_width": 2}
    draw.text((center_x + cyan_offset[0], center_y + cyan_offset[1]), "HyyAnk", fill=BG, stroke_fill=CYAN, font=display, **kwargs)
    draw.text((center_x + red_offset[0], center_y + red_offset[1]), "HyyAnk", fill=BG, stroke_fill=RED, font=display, **kwargs)
    draw.text((center_x, center_y), "HyyAnk", fill=PAPER, font=display, **kwargs)

    progress = min(1.0, frame / 19)
    line_end = 850 + int(215 * progress)
    draw.line((42, 352, line_end, 352), fill=RED, width=3)
    draw.line((42, 366, 690, 366), fill=CYAN, width=2)

    eye_x, eye_y = 1000, 248
    cycle = frame / total
    sharingan_rotation = (cycle * math.tau / 3) + (0.055 * math.sin(cycle * math.tau * 3))
    sharingan_pulse = (math.sin(cycle * math.tau * 2) + 1) / 2
    draw_mangekyou(draw, eye_x, eye_y, 108, sharingan_rotation, sharingan_pulse)

    scan_y = int(((frame * 15) % (height + 36)) - 18)
    draw.rectangle((0, scan_y, width, scan_y + 2), fill=(90, 104, 93))
    draw.text((886, 421), "MANGEKYOU MOTION", fill=MUTED, font=mono)
    draw.text((42, 422), "PRODUCT / VISUAL / MOTION / CODE", fill=MUTED, font=mono)
    return image


def cubic_point(t: float) -> tuple[float, float]:
    segments = [
        ((100, 154), (205, 35), (320, 35), (430, 116)),
        ((430, 116), (545, 262), (650, 262), (760, 192)),
        ((760, 192), (880, 35), (995, 35), (1100, 154)),
    ]
    segment = min(2, int(t * 3))
    local = (t * 3) - segment
    p0, p1, p2, p3 = segments[segment]
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
    for index, (x, y, label) in enumerate(labels):
        pulse = 1 + 0.25 * math.sin((frame / total) * math.tau * 2 + index)
        radius = int(25 * pulse)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=RED, width=2)
        draw.rectangle((x - 7, y - 7, x + 7, y + 7), fill=RED)
        draw.text((x - len(label) * 5.2, y + 44), label, fill=PAPER, font=font(FONT_DISPLAY, 16))
    runner_x, runner_y = cubic_point((frame / total) % 1)
    draw.ellipse((runner_x - 14, runner_y - 14, runner_x + 14, runner_y + 14), fill=CYAN)
    draw.ellipse((runner_x - 5, runner_y - 5, runner_x + 5, runner_y + 5), fill=PAPER)
    return image


def render_terminal(frame: int, total: int, width: int = 1200, height: int = 400) -> Image.Image:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height, spacing=92)

    card = (92, 42, 1108, 350)
    header_height = 72
    draw.rounded_rectangle(card, radius=18, fill=(33, 33, 33), outline=(101, 108, 104), width=2)
    draw.rounded_rectangle(
        (112, 62, 1088, 330),
        radius=12,
        fill=(5, 7, 7),
        outline=(73, 80, 76),
        width=1,
    )
    draw.rectangle((113, 63, 1087, 63 + header_height), fill=(28, 32, 31))
    draw.line((113, 63 + header_height, 1087, 63 + header_height), fill=(65, 74, 69), width=1)

    title_font = font(FONT_MONO, 25)
    command_font = font(FONT_MONO, 36)
    meta_font = font(FONT_MONO, 15)

    icon_x, icon_y = 143, 88
    draw.rounded_rectangle((icon_x, icon_y, icon_x + 28, icon_y + 28), radius=4, outline=CYAN, width=2)
    draw.line((icon_x + 7, icon_y + 9, icon_x + 13, icon_y + 14), fill=RED, width=2)
    draw.line((icon_x + 13, icon_y + 14, icon_x + 7, icon_y + 19), fill=RED, width=2)
    draw.line((icon_x + 16, icon_y + 20, icon_x + 22, icon_y + 20), fill=PAPER, width=2)
    draw.text((187, 88), "Terminal", fill=MUTED, font=title_font)

    copy_box = (1017, 81, 1063, 120)
    draw.rounded_rectangle(copy_box, radius=7, fill=(35, 40, 38), outline=(120, 128, 123), width=1)
    draw.rounded_rectangle((1030, 90, 1044, 105), radius=2, outline=MUTED, width=2)
    draw.rounded_rectangle((1036, 96, 1050, 111), radius=2, outline=RED, width=2)

    command = "npx create-HyyAnk-design"
    type_start = 8
    type_end = 43
    hold_end = 55
    if frame < type_start:
        visible_count = 0
    elif frame <= type_end:
        progress = (frame - type_start) / max(1, type_end - type_start)
        visible_count = min(len(command), 1 + int(progress * len(command)))
    elif frame <= hold_end:
        visible_count = len(command)
    else:
        erase_progress = (frame - hold_end) / max(1, total - hold_end - 1)
        visible_count = max(0, len(command) - int(erase_progress * len(command)))

    prompt_x, command_y = 155, 218
    draw.text((prompt_x, command_y), "~", fill=CYAN, font=command_font, anchor="lm")
    command_x = 202
    visible = command[:visible_count]
    first_token = visible[: min(3, len(visible))]
    rest = visible[3:] if len(visible) > 3 else ""
    draw.text((command_x, command_y), first_token, fill=RED, font=command_font, anchor="lm")
    first_width = draw.textlength(first_token, font=command_font)
    draw.text((command_x + first_width, command_y), rest, fill=PAPER, font=command_font, anchor="lm")
    typed_width = draw.textlength(visible, font=command_font)

    cursor_visible = (frame // 4) % 2 == 0 or (type_start <= frame <= type_end)
    if cursor_visible:
        cursor_x = command_x + typed_width + 5
        draw.rectangle((cursor_x, command_y - 23, cursor_x + 4, command_y + 24), fill=RED)

    draw.text((155, 293), "DESIGN SYSTEM INITIALIZER", fill=(118, 126, 121), font=meta_font)
    draw.text((861, 293), "HYYANK / LOCAL", fill=(118, 126, 121), font=meta_font)
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
        "Starting animation render | config=1200px canvas, 48-64 frames, 10fps | profiles=1 | mode=local-render | concurrency=1 | automation=Pillow-code-renderer-no-OS-input",
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
            render_asset("terminal-typing", 64, render_terminal, args.output_dir / "hyyank-terminal.gif", progress)
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
        f"Final summary | total=3 success=3 failed=0 skipped=0 retries=0 elapsed={elapsed:.2f}s",
        step="summary",
        style="success",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
