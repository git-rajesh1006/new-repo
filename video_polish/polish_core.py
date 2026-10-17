"""Shot list + zoom helpers shared by the polish scripts."""
# (start, end, zoom_from, zoom_to, focus_x, focus_y)   -- shots found with scene detection on the source
SHOTS = [(0.00, 2.80, 1.00, 1.08, .46, .55), (2.80, 3.30, 1.00, 1.00, .5, .5), (3.30, 5.12, 1.00, 1.06, .62, .42), (5.12, 6.76, 1.00, 1.05, .50, .45),
         (6.76, 8.44, 1.07, 1.00, .45, .55), (8.44, 8.70, 1.00, 1.00, .5, .5), (8.70, 10.40, 1.00, 1.06, .50, .45), (10.40, 12.70, 1.06, 1.00, .60, .45),
         (12.70, 15.28, 1.00, 1.06, .50, .45), (15.28, 16.80, 1.00, 1.05, .66, .45), (16.80, 99.0, 1.00, 1.05, .50, .45)]
def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)

def shot_params(T):
    for a, b, z0, z1, fx, fy in SHOTS:
        if a <= T < b: return lerp(z0, z1, ease((T - a) / max(1e-6, min(b, 18.3) - a))), fx, fy
    return 1.0, .5, .5
def lerp(a, b, t): return a + (b - a) * t

