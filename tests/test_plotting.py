"""Plotting helper tests (matplotlib optional extra)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from twistdiff.ode import Trajectory
from twistdiff.plotting import save_series_plot, save_trajectory_plot


def test_save_plots(tmp_path: Path):
    tt = np.linspace(0, 1, 11)
    traj = Trajectory(t=tt, y=np.column_stack([tt, np.zeros(11)]))
    p1 = save_trajectory_plot(traj, tmp_path / "osc.png", labels=["x", "v"], title="t")
    assert p1.exists() and p1.stat().st_size > 0
    p2 = save_series_plot(
        traj.t,
        {"a": traj.y[:, 0]},
        tmp_path / "series.png",
        title="s",
    )
    assert p2.exists()
