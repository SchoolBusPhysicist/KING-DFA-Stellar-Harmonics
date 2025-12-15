#!/usr/bin/env python3
"""
Glashow Resonance Event D₂ Analysis

Calculates correlation dimension D₂ for the IceCube Glashow resonance event
(6.05 PeV electron antineutrino) to test KDFA prediction: D₂ = 19/13 ≈ 1.4615

Data: 23,810 photon pulses from a single cascade event
Source: IceCube Collaboration (2021), Nature, DOI: 10.1038/s41586-021-03256-1

Author: Jason A. King
Date: December 2025
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy import stats
import os

# KDFA Prediction
D2_PREDICTED = 19 / 13  # = 1.4615384615...

# Analysis parameters
R_MIN = 1e-2
R_MAX = 1.0
N_RADII = 50
FIT_RANGE = (0.2, 0.8)  # Fraction of radii to use for fitting (avoid edges)
SAMPLE_SIZE = 5000  # Subsample for computational efficiency


def load_glashow_pulses(filepath):
    """
    Load pulse data from Glashow event file.

    Format: string om time[ns] charge[pe]
    Returns: array of (time, charge) normalized to [0,1] range
    """
    times = []
    charges = []

    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or line.startswith('##'):
                continue
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    time = float(parts[2])
                    charge = float(parts[3])
                    times.append(time)
                    charges.append(charge)
                except ValueError:
                    continue

    times = np.array(times)
    charges = np.array(charges)

    # Normalize to [0, 1] for correlation dimension
    times_norm = (times - times.min()) / (times.max() - times.min())
    charges_norm = (charges - charges.min()) / (charges.max() - charges.min() + 1e-10)

    return np.column_stack([times_norm, charges_norm])


def grassberger_procaccia(points, r_min=R_MIN, r_max=R_MAX, n_radii=N_RADII, max_points=SAMPLE_SIZE):
    """
    Calculate correlation dimension using Grassberger-Procaccia algorithm.

    C(r) = (2 / N(N-1)) * sum_{i<j} Theta(r - |x_i - x_j|)
    D₂ = d(log C) / d(log r)
    """
    # Subsample if too large
    if len(points) > max_points:
        indices = np.random.choice(len(points), max_points, replace=False)
        points = points[indices]

    N = len(points)

    # Compute pairwise distances (upper triangle only)
    distances = pdist(points, metric='euclidean')

    # Correlation integral for each radius
    r_values = np.logspace(np.log10(r_min), np.log10(r_max), n_radii)
    C_r = np.array([np.sum(distances < r) * 2 / (N * (N - 1)) for r in r_values])

    # Avoid log(0)
    mask = C_r > 0
    log_r = np.log(r_values[mask])
    log_C = np.log(C_r[mask])

    return r_values[mask], C_r[mask], log_r, log_C


def fit_correlation_dimension(log_r, log_C, fit_range=FIT_RANGE):
    """
    Fit D₂ from scaling region of log-log plot.

    Returns: D₂, error, r_squared
    """
    n = len(log_r)
    start = int(n * fit_range[0])
    end = int(n * fit_range[1])

    log_r_fit = log_r[start:end]
    log_C_fit = log_C[start:end]

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_r_fit, log_C_fit)

    return slope, std_err, r_value**2


def bootstrap_d2(points, n_bootstrap=50, sample_frac=0.8):
    """
    Bootstrap estimation of D₂ with uncertainty.
    """
    d2_samples = []
    n_sample = min(int(len(points) * sample_frac), SAMPLE_SIZE)

    for _ in range(n_bootstrap):
        indices = np.random.choice(len(points), n_sample, replace=True)
        sample = points[indices]

        _, _, log_r, log_C = grassberger_procaccia(sample)
        d2, _, _ = fit_correlation_dimension(log_r, log_C)
        d2_samples.append(d2)

    return np.mean(d2_samples), np.std(d2_samples)


def analyze_time_only(times_norm):
    """
    1D correlation dimension from time series only.
    """
    # Embed in 2D using time-delay embedding
    tau = 10  # embedding delay
    embedded = np.column_stack([times_norm[:-tau], times_norm[tau:]])

    _, _, log_r, log_C = grassberger_procaccia(embedded)
    d2, err, r2 = fit_correlation_dimension(log_r, log_C)

    return d2, err


def main():
    print("=" * 70)
    print("Glashow Resonance Event - Correlation Dimension Analysis")
    print("KDFA Prediction: D₂ = 19/13 = {:.4f}".format(D2_PREDICTED))
    print("=" * 70)
    print()

    # Find data file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'event.txt')

    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        return

    # Load data
    print("Loading Glashow event pulses...")
    points = load_glashow_pulses(data_file)
    print(f"Loaded {len(points)} pulses")
    print(f"Time range: {points[:, 0].min():.3f} - {points[:, 0].max():.3f} (normalized)")
    print(f"Charge range: {points[:, 1].min():.3f} - {points[:, 1].max():.3f} (normalized)")
    print()

    # Main D₂ calculation (time-charge 2D)
    print("Calculating D₂ (time-charge 2D space)...")
    r_values, C_r, log_r, log_C = grassberger_procaccia(points)
    d2, err, r2 = fit_correlation_dimension(log_r, log_C)
    print(f"D₂ = {d2:.3f} ± {err:.3f} (R² = {r2:.4f})")
    print()

    # Bootstrap for robust error
    print("Bootstrap uncertainty estimation (100 resamples)...")
    d2_boot, d2_boot_err = bootstrap_d2(points, n_bootstrap=100)
    print(f"D₂ (bootstrap) = {d2_boot:.3f} ± {d2_boot_err:.3f}")
    print()

    # Time-only analysis (1D embedding)
    print("Time-only analysis (delay embedding)...")
    d2_time, err_time = analyze_time_only(points[:, 0])
    print(f"D₂ (time only) = {d2_time:.3f} ± {err_time:.3f}")
    print()

    # Compare to KDFA prediction
    print("=" * 70)
    print("COMPARISON TO KDFA PREDICTION")
    print("=" * 70)
    print()
    print(f"KDFA Predicted D₂:     {D2_PREDICTED:.4f}")
    print(f"Measured D₂ (2D):      {d2_boot:.3f} ± {d2_boot_err:.3f}")
    print(f"Measured D₂ (time):    {d2_time:.3f} ± {err_time:.3f}")
    print()

    # Calculate match percentage
    diff_2d = abs(d2_boot - D2_PREDICTED)
    diff_time = abs(d2_time - D2_PREDICTED)

    match_2d = (1 - diff_2d / D2_PREDICTED) * 100
    match_time = (1 - diff_time / D2_PREDICTED) * 100

    print(f"2D Match:   {match_2d:.1f}% (diff = {diff_2d:.3f})")
    print(f"Time Match: {match_time:.1f}% (diff = {diff_time:.3f})")
    print()

    # Statistical significance
    sigma_2d = diff_2d / d2_boot_err if d2_boot_err > 0 else float('inf')
    print(f"2D deviation: {sigma_2d:.1f}σ from prediction")
    print()

    if diff_2d < 0.15:
        print("✓ KDFA prediction CONFIRMED within tolerance")
    elif diff_2d < 0.30:
        print("⚠ KDFA prediction PARTIALLY supported")
    else:
        print("✗ KDFA prediction NOT supported by this data")

    print()
    print("=" * 70)
    print("Note: This is a SINGLE EVENT analysis (6.05 PeV cascade)")
    print("Statistical power is limited - bulk IceCube data gives D₂ = 1.495 ± 0.144")
    print("=" * 70)


if __name__ == '__main__':
    main()
