"""Optional matplotlib helpers (import only when plotting extras installed)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from twistdiff.ode import Trajectory


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "matplotlib is required for plotting; install with: pip install 'twistdiff[plot]'"
        ) from exc
    return plt


def save_trajectory_plot(
    traj: Trajectory,
    path: str | Path,
    *,
    labels: list[str] | None = None,
    title: str = "",
    xlabel: str = "t",
) -> Path:
    """Save state vs time to ``path`` (PNG recommended)."""
    plt = _require_matplotlib()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = traj.y.shape[1]
    if labels is None:
        labels = [f"y[{i}]" for i in range(n)]
    if len(labels) != n:
        raise ValueError("labels length must match state dimension")

    fig, ax = plt.subplots(figsize=(7, 4))
    for i in range(n):
        ax.plot(traj.t, traj.y[:, i], label=labels[i])
    ax.set_xlabel(xlabel)
    ax.set_ylabel("state")
    if title:
        ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def save_series_plot(
    t: np.ndarray,
    series: dict[str, np.ndarray],
    path: str | Path,
    *,
    title: str = "",
    xlabel: str = "t",
    ylabel: str = "",
) -> Path:
    """Save named 1-D series vs time."""
    plt = _require_matplotlib()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, y in series.items():
        ax.plot(t, y, label=name)
    ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
