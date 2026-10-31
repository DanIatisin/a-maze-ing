import os
from typing import Any
from collections.abc import Callable

from mlx import Mlx

from mazegen import MazeGenerator


MAX_W: int = 1200  # larghezza massima dell'immagine in pixel
MAX_H: int = 800  # altezza massima dell'immagine in pixel
LEGEND_H: int = 80  # fascia sotto il maze per la legenda dei tasti
MIN_CELL: int = 2  # dimensione minima di una cella in pixel
BACKGROUND: tuple[int, int, int] = (35, 0, 35)


class DisplayError(Exception):
    """Gestisce gli errori di MLX"""


def fill_rect(
    data: memoryview,
    size_line: int,
    bpp: int,
    fmt: int,
    x: int,
    y: int,
    w: int,
    h: int,
    rgb: tuple[int, int, int],
) -> None:
    """Riempe un rettangolo con un colore RGB.

    Args:
        data: buffer dell'immagine creata con mlx_get_data_addr.
        size_line: byte per riga.
        bpp: bits per pixel.
        fmt: formato dei colori RGB (0 = B8G8R8A8, 1 = A8R8G8B8).
        x: lato sinistro del rettangolo in pixels.
        y: lato in alto del rettangolo in pixels.
        w: larghezza del rettangolo in pixels.
        h: altezza del rettangolo in pixels.
        rgb: colore (red, green, blue).
    """
    r, g, b = rgb
    if fmt == 0:
        pixel = bytes((b, g, r, 255))
    else:
        pixel = bytes((255, r, g, b))
    step = bpp // 8
    row = pixel * w
    for yy in range(y, y + h):
        offset = yy * size_line + x * step
        data[offset : offset + w * step] = row
        

class MlxDisplay:
    
    def __init__(self, gen: MazeGenerator,
                 regenerate: Callable[[], None]) -> None:
        self.maze: MazeGenerator = gen
        self.regenerate: Callable[[], None] = regenerate

        self.show_path: bool = True
        self.wall_idx: int = 0
        self.pattern_idx: int = 0
        
        self.cell: int = max(MIN_CELL, min(MAX_W // gen.width, MAX_H // gen.height))
        self.wall: int = max(1, self.cell // 8)
        self.img_w: int = gen.width * self.cell
        self.img_h: int = gen.height * self.cell
        
        self.m: Any = Mlx()
        self.mlx_ptr: Any = self.m.mlx_init()
        if not self.mlx_ptr:
            raise DisplayError("MLX could not connect to the display")
        self.win: Any = self.m.mlx_new_window(
            self.mlx_ptr, self.img_w, self.img_h + LEGEND_H, "A-Maze-ing"
        )
        if not self.win:
            raise DisplayError("MLX could not create the window")
        self.img: Any = self.m.mlx_new_image(self.mlx_ptr, self.img_w, self.img_h)
        if not self.img:
            raise DisplayError("MLX could not create the image")

    def draw(self) -> None:
        """Riempe l'immagine con un colore"""
        data, bpp, size_line, fmt = self.m.mlx_get_data_addr(self.img)
        fill_rect(data, size_line, bpp, fmt, 0, 0, self.img_w, self.img_h, BACKGROUND)
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win, self.img, 0, 0)
    
    def on_close(self, param: Any) -> None:
        """Interrompe il loop quando la finestra viene chiusa"""
        self.m.mlx_loop_exit(self.mlx_ptr)

    def on_key(self, keynum: int, param: Any) -> None:
        """Compie determinate azioni in base al tasto premuto sulla tastiera
        65307 = ESC
        49 = 1"""
        print(keynum)
        if keynum == 65307:
            self.on_close("ESC premuto")
        if keynum == 49:
            print("1.Genero nuovo maze")
        if keynum == 50:
            self.show_path = False
            print("2.Nascondo/mostro maze")
        if keynum == 51:
            print("3.Cambio colore muri")
        if keynum == 52:
            print("4.Cambio colore 42")
        if keynum == 53:
            print("5.Esci")
            self.on_close("5.Esci premuto")

    def on_mouse(self, button, x, y, param):
        print(f"Button {button} clicked at ({x}, {y})")

    def run(self) -> None:
        """Visualizza l'immagine, registra gli input e chiude la finestra"""
        try:
            self.draw()
            self.m.mlx_key_hook(self.win, self.on_key, None)
            self.m.mlx_mouse_hook(self.win, self.on_mouse, None)
            self.m.mlx_hook(self.win, 33, 0, self.on_close, None)
            self.m.mlx_loop(self.mlx_ptr)
        finally:
            self.close()
            
    def close(self) -> None:
        """Elimina immagine, finestra e pointer"""
        self.m.mlx_destroy_image(self.mlx_ptr, self.img)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win)
        self.m.mlx_release(self.mlx_ptr)


