# Contributing

Contributions are welcome! This list aims to track papers, code, and datasets on **underwater visual enhancement (UVE)** and **underwater 3D reconstruction** (SfM / MVS / SLAM / NeRF / 3D Gaussian Splatting).

## How to contribute

1. Fork this repository and create a new branch.
2. Add your entry to the appropriate section of `README.md`, keeping entries **sorted by year (ascending)**.
3. Open a pull request with a short description of the added work.

## Entry format

Please follow the existing table format:

```markdown
| 2024 | CVPR | Paper Title | [Paper](https://arxiv.org/abs/xxxx.xxxxx) / [Code](https://github.com/user/repo) | Acronym |
```

Guidelines:

- **Paper link**: prefer the arXiv abstract page (`https://arxiv.org/abs/...`); otherwise use the official publisher/DOI page.
- **Code link**: only link the *official* implementation. Leave it out if no official code is released.
- **Venue**: use the short name of the venue of the accepted version (CVPR, ICCV, TIP, TPAMI, ...); use `arXiv` for preprints.
- New categories/sections are welcome if a group of works does not fit the existing taxonomy — please explain the rationale in the PR.

## Scope

In scope: underwater image/video enhancement and restoration, underwater color correction, physics-based underwater imaging models, underwater SfM/MVS/SLAM, NeRF and 3DGS in underwater or scattering media, underwater datasets, and evaluation metrics used in this field.

Out of scope: general-purpose enhancement/reconstruction works with no underwater or scattering-media relevance (foundational works such as NeRF or 3DGS are listed only as context).

## Reporting issues

Found a broken link, a wrong venue, or a misplaced entry? Please open an issue — it helps keep the list reliable.
