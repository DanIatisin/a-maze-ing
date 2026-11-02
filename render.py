from typing import Any
from collections.abc import Callable

from mlx import Mlx

from mazegen import MazeGenerator, N, E, S, W


MARGIN_H: int = 120  # barra del titolo, taskbar, ecc.
MARGIN_W: int = 40   # bordi della finestra
LEGEND_W: int = 80   # bordo per i tasti
MIN_CELL: int = 4    # dimensione minima di una cella in pixel
BACKGROUND: list[tuple[int, int, int]] = [
    (35, 0, 35),  # Viola
    (35, 0, 0),   # Rosso
    (35, 35, 0),  # Giallo
    (0, 35, 0),   # Verde
    (0, 35, 35),  # Celeste
    (0, 0, 35),   # Blu
]
WALL_COLORS: list[tuple[int, int, int]] = [
    (200, 0, 175),  # Viola
    (255, 0, 0),    # Rosso
    (255, 255, 0),  # Giallo
    (0, 255, 0),    # Verde
    (0, 255, 255),  # Celeste
    (0, 0, 255),    # Blu
]
PATTERN_COLORS: list[tuple[int, int, int]] = [
    (255, 255, 255),  # Bianco
    (0, 0, 0),        # Nero
    (255, 192, 41),   # Giallo
    (172, 38, 255),   # Viola
]
START_COLOR: tuple[int, int, int] = (0, 220, 120)
END_COLOR: tuple[int, int, int] = (255, 0, 0)
PATH_COLOR: tuple[int, int, int] = (220, 200, 0)

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
        data[offset: offset + w * step] = row


class MlxDisplay:

    def __init__(self, gen: MazeGenerator,
                 regenerate: Callable[[], None]) -> None:

        self.gen: MazeGenerator = gen
        self.regenerate: Callable[[], None] = regenerate

        self.show_path: bool = True
        self.wall_idx: int = 0
        self.pattern_idx: int = 0

        self.m: Any = Mlx()
        self.mlx_ptr: Any = self.m.mlx_init()
        if not self.mlx_ptr:
            raise DisplayError("MLX could not connect to the display")

        # Leggo la dimensione dello schermo e adatto la grandezza dell'immagine
        _, screen_w, screen_h = self.m.mlx_get_screen_size(self.mlx_ptr)
        max_w = screen_w - MARGIN_W - LEGEND_W
        max_h = screen_h - MARGIN_H
        self.cell: int = min(32, max_w // gen.width, max_h // gen.height)
        if self.cell < MIN_CELL:
            raise DisplayError(
                f"Maze {gen.width}x{gen.height} is too large for the "
                f"screen ({screen_w}x{screen_h})")
        self.wall: int = 1
        self.img_w: int = gen.width * self.cell
        self.img_h: int = gen.height * self.cell

        self.win: Any = self.m.mlx_new_window(
            self.mlx_ptr, self.img_w + LEGEND_W, self.img_h, "A-Maze-ing"
        )
        if not self.win:
            raise DisplayError("MLX could not create the window")
        self.img: Any = self.m.mlx_new_image(
            self.mlx_ptr, self.img_w, self.img_h)
        if not self.img:
            raise DisplayError("MLX could not create the image")

    def _draw_walls(self, data: Any, size_line: int,
                    bpp: int, fmt: int) -> None:
        """Disegna i muri di ogni cella"""
        color = WALL_COLORS[self.wall_idx]
        c = self.cell
        t = self.wall

        def fill(x: int, y: int, t: int, h: int) -> None:
            fill_rect(data, size_line, bpp, fmt, x, y, t, h, color)

        for y, row in enumerate(self.gen.maze):
            for x, value in enumerate(row):
                cx, cy = c * x, c * y
                if value & N:
                    fill(cx, cy, c, t)
                if value & E:
                    fill(cx + c - t, cy, t, c)
                if value & S:
                    fill(cx, cy + c - t, c, t)
                if value & W:
                    fill(cx, cy, t, c)

    def _draw_path(
                self, data: Any, size_line: int, bpp: int, fmt: int) -> None:
        """Disegna la soluzione"""
        path_color = PATH_COLOR
        start_color = START_COLOR
        end_color = END_COLOR
        c = self.cell
        x, y = self.gen.entry_pos[0], self.gen.entry_pos[1]
        fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, start_color)

        for direction in self.gen.path:
            if direction == "N":
                y -= 1
            if direction == "E":
                x += 1
            if direction == "S":
                y += 1
            if direction == "W":
                x -= 1
            fill_rect(
                data, size_line, bpp, fmt, x * c, y * c, c, c, path_color)
        fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, end_color)

    def _draw_42(self, data: Any, size_line: int,
                 bpp: int, fmt: int) -> None:
        """Riempe il pattern 42 di un colore"""
        color = PATTERN_COLORS[self.pattern_idx]
        c = self.cell

        for x, y in self.gen.pattern_cords:
            fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, color)

    def draw(self) -> None:
        """Disegna il maze, il pattern 42 e la soluzione"""
        data, bpp, size_line, fmt = self.m.mlx_get_data_addr(self.img)
        fill_rect(
            data, size_line, bpp, fmt, 0, 0, self.img_w,
            self.img_h, BACKGROUND[self.wall_idx])
        self._draw_42(data, size_line, bpp, fmt)
        if self.show_path is True:
            self._draw_path(data, size_line, bpp, fmt)
        self._draw_walls(data, size_line, bpp, fmt)
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win, self.img, 0, 0)

    def on_close(self, param: Any) -> None:
        """Interrompe il loop quando la finestra viene chiusa"""
        self.m.mlx_loop_exit(self.mlx_ptr)

    def on_key(self, keynum: int, param: Any) -> None:
        """Compie determinate azioni in base al tasto premuto sulla tastiera
        65307 = ESC
        49 = 1 ecc..."""
        print(keynum)
        if keynum == 65307:
            self.on_close("ESC premuto")
        if keynum == 49:
            print("1.Genero nuovo maze")
        if keynum == 50:
            self.show_path = not self.show_path
            self.draw()
            print("2.Nascondo/mostro path")
        if keynum == 51:
            print("3.Cambio colore muri")
            self.wall_idx = (self.wall_idx + 1) % len(WALL_COLORS)
            self.draw()
        if keynum == 52:
            print("4.Cambio colore 42")
            self.pattern_idx = (self.pattern_idx + 1) % len(PATTERN_COLORS)
            self.draw()

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
