from src.main_loop import main
from src.render.camera import draw_triangle_numba

import numpy as np

def warmup_numba():
    dummy_pixels = np.zeros((10, 10, 3), dtype=np.uint8)
    dummy_tex = np.zeros((4, 4, 3), dtype=np.uint8)
    dummy_alpha = np.ones((4, 4), dtype=np.uint8)
    dummy_zbuffer = np.full((10, 10), np.inf, dtype=np.float64)
    dummy_lights = [(
        np.array([0.0, 0.0, 0.0]),
        1.0,
        np.array([1.0, 1.0, 1.0]),
        10.0
    )]
    dummy_vec = np.array([0.0, 0.0, 1.0])

    draw_triangle_numba(
        dummy_pixels, dummy_tex, dummy_alpha, dummy_zbuffer,
        10, 10,
        1.0, 1.0, 1.0, 0.0, 0.0,
        2.0, 1.0, 1.0, 1.0, 0.0,
        1.0, 2.0, 1.0, 0.5, 1.0,
        0.0, 0.0,
        1.0, 0.0,
        0.5, 1.0,
        1, 1.0,
        np.array([0.0, 0.0, 0.0]),
        dummy_lights,
        dummy_vec, dummy_vec, dummy_vec
    )
    print("Numba compilation terminée.")

if __name__ == "__main__":
    warmup_numba()
    main()