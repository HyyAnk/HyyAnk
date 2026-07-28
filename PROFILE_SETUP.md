# GitHub profile setup

The README establishes the visual direction. These account-level changes will make the full profile support the same Designer-first positioning.

## Profile bio

Use this as the short GitHub bio:

> Designer crafting clear interfaces and useful digital products. I prototype with code.

Keep the location as `Vietnam`. Use one consistent X handle everywhere. The public profile currently shows `@0x_HyyAnk`, while the previous README linked to `@jnhoanganh`.

## Recommended pinned repositories

Pin these in this order:

1. `Merge-Board-Node`
2. `Photo-ID-Studio`
3. `Pdf-business-card-stamper`
4. `Image-video-Google-API---Aistudio`

Keep trading bots and forks out of the first row. They can remain public, but they weaken the first Designer-focused impression.

## Repository descriptions

Suggested one-line descriptions:

- `Merge-Board-Node`: Local-first visual workspace for organizing images and text in the browser.
- `Photo-ID-Studio`: Focused browser tool for preparing precise photo ID assets.
- `Pdf-business-card-stamper`: Print workflow utility for placing business-card content into PDFs.
- `Image-video-Google-API---Aistudio`: Interface experiment for AI image and video generation.

## Project presentation checklist

For each pinned repository, add:

- One strong 1600 x 900 cover image
- A one-sentence problem statement
- Three to five screens showing the main flow
- A short section for decisions and tradeoffs
- A live demo link when available
- Consistent repository topics such as `product-design`, `creative-tools`, `react`, and `typescript`

The cover image matters more than additional badges or GitHub statistics. A recruiter should understand the product and your role before reading implementation details.

## Animation setup

The profile README uses `hyyank-hero.gif` for the coded wordmark and `design-process.gif` for the process diagram. GitHub renders animated GIFs in README images, while SVG files are kept as editable source art direction.

The repository also includes `.github/workflows/snake.yml`. It runs on pushes to `main`, on a daily schedule, or manually from the Actions tab and publishes the contribution animation to the `output` branch. If the snake is not visible immediately after the first push, open **Actions**, run **Generate contribution animation**, then refresh the profile.
