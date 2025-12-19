#!/usr/bin/env python3
"""
Generate triangular geometry diagram showing S-R-Interface structure.
TFA Framework - Figure for paper.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

def generate_triangular_geometry():
    """Generate diagram showing triangular S-R-Interface structure with nested depth."""

    fig, ax = plt.subplots(figsize=(12, 10))

    # Main triangle vertices
    S = np.array([0.5, 0.93])      # Top - Structure
    R = np.array([0.1, 0.2])       # Bottom left - Relation
    I = np.array([0.9, 0.2])       # Bottom right - Interface

    # Draw main triangle
    triangle = plt.Polygon([S, R, I], fill=False, edgecolor='black', linewidth=3)
    ax.add_patch(triangle)

    # Fill zones
    # Zone 1 (S-dominated) - top region
    zone1 = plt.Polygon([S, [0.3, 0.56], [0.7, 0.56]],
                         facecolor='lightblue', alpha=0.5, edgecolor='none')
    ax.add_patch(zone1)

    # Zone 2 (Generative) - middle region
    zone2 = plt.Polygon([[0.3, 0.56], [0.7, 0.56], [0.8, 0.35], [0.2, 0.35]],
                         facecolor='lightgreen', alpha=0.5, edgecolor='none')
    ax.add_patch(zone2)

    # Zone 3 (R-dominated) - bottom region
    zone3 = plt.Polygon([[0.2, 0.35], [0.8, 0.35], I, R],
                         facecolor='lightyellow', alpha=0.5, edgecolor='none')
    ax.add_patch(zone3)

    # Draw nested triangles (powers of 3)
    def draw_nested(center, size, depth, max_depth=3):
        if depth > max_depth:
            return
        # Smaller triangle
        offset = size * 0.3
        s = center + np.array([0, offset])
        r = center + np.array([-offset * 0.866, -offset * 0.5])
        i = center + np.array([offset * 0.866, -offset * 0.5])

        alpha = 0.7 - depth * 0.15
        tri = plt.Polygon([s, r, i], fill=False, edgecolor='darkblue',
                          linewidth=2-depth*0.5, alpha=alpha, linestyle='--')
        ax.add_patch(tri)

        # Recurse into each sub-triangle
        if depth < max_depth:
            for vertex in [s, r, i]:
                draw_nested((center + vertex) / 2, size * 0.5, depth + 1, max_depth)

    # Draw nested structure from center
    center = (S + R + I) / 3
    draw_nested(center, 0.35, 1, 3)

    # Labels for vertices
    ax.annotate('S\n(Structure)', S, fontsize=14, ha='center', va='bottom',
                fontweight='bold', color='darkblue')
    ax.annotate('R\n(Relation)', R + np.array([-0.05, -0.05]), fontsize=14,
                ha='center', va='top', fontweight='bold', color='darkgreen')
    ax.annotate('Interface\n(Measurement)', I + np.array([0.05, -0.05]), fontsize=14,
                ha='center', va='top', fontweight='bold', color='darkred')

    # Zone labels
    ax.text(0.5, 0.75, 'Zone 1: κ < 1/e\nS dominates', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(0.5, 0.45, 'Zone 2: 1/e ≤ κ < 0.65\nGENERATIVE', ha='center', fontsize=12,
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(0.5, 0.25, 'Zone 3: κ ≥ 0.65\nR dominates', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Powers of 3 annotation
    powers_text = ('Nested Depth (Powers of 3):\n'
                   '3¹ = S, R, Interface\n'
                   '3² = 9 sub-couplings\n'
                   '3³ = 27 micro-states\n'
                   '3ᵐ = fractal depth m')
    ax.text(0.02, 0.98, powers_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    # Key equation
    eq_text = 'X = n/(3ᵐ) + p/(27q) × (D₂ − 1)'
    ax.text(0.5, 0.02, eq_text, transform=ax.transAxes, fontsize=13,
            ha='center', fontweight='bold', style='italic',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.9))

    # D₂ = 19/13 annotation
    d2_text = ('D₂ = 19/13\n'
               '19: hexagonal packing\n'
               '13: orthogonal frames')
    ax.text(0.98, 0.98, d2_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.9))

    # Title
    ax.set_title('TFA Triangular Geometry: S-R-Interface Coupling\n'
                 'The minimal structure for generative dynamics', fontsize=14)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0.05, 1.05)
    ax.set_aspect('equal')
    ax.axis('off')

    # Save
    output_dir = Path(__file__).parent.parent / 'results' / 'stellar'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'triangular_geometry.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")
    plt.close()

if __name__ == "__main__":
    generate_triangular_geometry()
