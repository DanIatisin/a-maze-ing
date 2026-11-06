import sys
from collections.abc import Callable
from typing import Any

from mlx import Mlx

from mazegen import E, MazeGenerator, N, S, W

MAX_SCREEN_W = 1920
MAX_SCREEN_H = 1080
MARGIN_H: int = 80  # barra del titolo, taskbar, ecc.
MARGIN_W: int = 40   # bordi della finestra
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
BUTTONS: list[tuple[str, str]] = [
    ("1", "Generate a new maze"),
    ("2", "Hide/show shortest path"),
    ("3", "Change maze color"),
    ("4", "Change 42 color"),
    ("ESC", "Close"),
]
TEXT_COLOR: int = 0xFFFFFFFF
LEGEND_W: int = 310   # bordo per i tasti
LEGEND_MARGIN: int = 15  # margine interno
ROW_H: int = 10       # altezza di una riga di testo
LEGEND_H: int = 2 * LEGEND_MARGIN + ROW_H * len(BUTTONS)

BTN_GAP: int = 10  # spazio tra i bottoni
BTN_MIN_H: int = 30
TEXT_PAD_X: int = 10  # margine del testo dentro il bottone


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
    """Classe che gestisce la visualizzazione del maze in MLX"""
    frames: int = 0
    def __init__(self, gen: MazeGenerator,
                 regenerate: Callable[[], MazeGenerator]) -> None:
        """Inizializza la visualizzazione del maze in MLX.

        Args:
            gen: oggetto MazeGenerator da visualizzare.
            regenerate: funzione che genera un nuovo maze.

        Raises:
            DisplayError: se MLX non riesce a generare l'immagine.
        """
        self.frames = 0
        self.gen: MazeGenerator = gen
        self.regenerate: Callable[[], MazeGenerator] = regenerate

        self.show_path: bool = True
        self.wall_idx: int = 0
        self.pattern_idx: int = 0

        self.m: Any = Mlx()
        self.mlx_ptr: Any = self.m.mlx_init()
        if not self.mlx_ptr:
            raise DisplayError("MLX could not connect to the display")

        # Leggo la dimensione dello schermo e adatto la grandezza dell'immagine
        _, screen_w, screen_h = self.m.mlx_get_screen_size(self.mlx_ptr)
        max_w = min(screen_w, MAX_SCREEN_W) - MARGIN_W - LEGEND_W
        max_h = min(screen_h, MAX_SCREEN_H) - MARGIN_H
        self.cell: int = min(96, max_w // gen.width, max_h // gen.height)
        if self.cell < MIN_CELL:
            raise DisplayError(
                f"Maze {gen.width}x{gen.height} is too large for the screen. "
                f"Max size: {int(max_w / MIN_CELL)}x{int(max_h / MIN_CELL)}"
            )
        self.wall: int = 1
        self.img_w: int = gen.width * self.cell
        self.img_h: int = gen.height * self.cell
        self.win: Any = self.m.mlx_new_window(
            self.mlx_ptr, self.img_w + LEGEND_W,
            max(self.img_h, LEGEND_H), "A-Maze-ing"
        )
        if not self.win:
            raise DisplayError("MLX could not create the window")
        self.img: Any = self.m.mlx_new_image(
            self.mlx_ptr, self.img_w, self.img_h)
        if not self.img:
            raise DisplayError("MLX could not create the image")
        self.panel: Any = self.m.mlx_new_image(
            self.mlx_ptr, LEGEND_W, self.img_h)
        if not self.panel:
            raise DisplayError("MLX could not create the panel image")

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
        c = self.cell
        x, y = self.gen.entry_pos[0], self.gen.entry_pos[1]
        fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, START_COLOR)

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
              data, size_line, bpp, fmt, x * c, y * c, c, c, PATH_COLOR)
        fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, END_COLOR)

    def _draw_42(self, data: Any, size_line: int,
                 bpp: int, fmt: int) -> None:
        """Riempe il pattern 42 di un colore"""
        color = PATTERN_COLORS[self.pattern_idx]
        c = self.cell

        for x, y in self.gen.pattern_cords:
            fill_rect(data, size_line, bpp, fmt, x * c, y * c, c, c, color)

    def _button_rect(self, index: int) -> tuple[int, int, int, int]:
        """Ritorna (x, y, width, height) di un pulsante"""
        n = len(BUTTONS)
        button = (self.img_h - 2 * LEGEND_MARGIN + BTN_GAP) // n
        h = max(BTN_MIN_H, button - BTN_GAP)
        buttons_area = n * h + (n - 1) * BTN_GAP
        topbutton = (self.img_h - buttons_area) // 2
        y = topbutton + index * (h + BTN_GAP)
        return LEGEND_MARGIN, y, LEGEND_W - 2 * LEGEND_MARGIN, h

    def _draw_panel(self) -> None:
        """Disegna il pannello della legenda ed ogni pulsante"""
        data, bpp, size_line, fmt = self.m.mlx_get_data_addr(self.panel)
        fill_rect(
            data, size_line, bpp, fmt,
            0, 0, LEGEND_W, self.img_h, BACKGROUND[self.wall_idx])
        for i in range(len(BUTTONS)):
            x, y, w, h = self._button_rect(i)
            fill_rect(
                data, size_line, bpp, fmt,
                x, y, w, h, WALL_COLORS[self.wall_idx])
            fill_rect(data, size_line, bpp, fmt,
                      x + 2, y + 2, w - 4, h - 4, BACKGROUND[self.wall_idx])

    def _write_buttons(self) -> None:
        """Scrive la leggenda dei comandi del maze"""
        for i, (key, label) in enumerate(BUTTONS):
            x, y, _, h = self._button_rect(i)
            self.m.mlx_string_put(
                self.mlx_ptr,
                self.win,
                self.img_w + x + TEXT_PAD_X,  # x
                y + (h - ROW_H) // 2,         # y
                TEXT_COLOR,
                f"{key}. {label}",
            )

    def draw(self) -> None:
        """Riempie i buffer delle immagini (senza toccare la finestra)"""
        data, bpp, size_line, fmt = self.m.mlx_get_data_addr(self.img)
        fill_rect(
            data, size_line, bpp, fmt, 0, 0, self.img_w,
            self.img_h, BACKGROUND[self.wall_idx])
        self._draw_42(data, size_line, bpp, fmt)
        if self.show_path is True:
            self._draw_path(data, size_line, bpp, fmt)
        self._draw_walls(data, size_line, bpp, fmt)
        self._draw_panel()
        self.present()

    def present(self) -> None:
        """Mette le immagini e il testo nella finestra"""
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win, self.img, 0, 0)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win, self.panel, self.img_w, 0)
        self._write_buttons()
    
    def on_loop(self, param: Any) -> None:
        """Ripresenta le immagini nei primi frame"""
        if self.frames < 30:
            self.frames += 1
            self.present()

    def on_expose(self, param: Any) -> None:
        """Ripresenta le immagini quando la finestra viene esposta"""
        self.present()

    def on_close(self, param: Any) -> None:
        """Interrompe il loop quando la finestra viene chiusa"""
        self.m.mlx_loop_exit(self.mlx_ptr)

    def _do_action(self, name: str) -> None:
        """Esegue le azioni scelte con la tastiera o col mouse."""
        if name == "1":
            try:
                self.gen = self.regenerate()
            except (ValueError, RuntimeError, OSError) as e:
                print(f"Error: {e}", file=sys.stderr)
                return
            self.draw()
        if name == "2":
            self.show_path = not self.show_path
            self.draw()
        if name == "3":
            self.wall_idx = (self.wall_idx + 1) % len(WALL_COLORS)
            self.draw()
        if name == "4":
            self.pattern_idx = (self.pattern_idx + 1) % len(PATTERN_COLORS)
            self.draw()
        if name == "ESC":
            self.on_close("ESC premuto")

    def on_key(self, keynum: int, param: Any) -> None:
        """Seleziona l'azione da compiere in base
        al tasto premuto sulla tastiera:
        65307 = ESC
        49 = 1 ecc..."""
        if keynum == 65307:
            self._do_action("ESC")
        if keynum == 49:
            self._do_action("1")
        if keynum == 50:
            self._do_action("2")
        if keynum == 51:
            self._do_action("3")
        if keynum == 52:
            self._do_action("4")

    def on_mouse(self, button: int, x: int, y: int, param: Any) -> None:
        """Registra l'azione premuta con il mouse"""
        if button != 1 or x < self.img_w:
            return
        panel_x = x - self.img_w
        for i, (key, _) in enumerate(BUTTONS):
            bx, by, bw, bh = self._button_rect(i)
            if bx <= panel_x < bw + bx and by <= y <= by + bh:
                self._do_action(key)
                return

    def run(self) -> None:
        try:
            self.draw()
            self.m.mlx_key_hook(self.win, self.on_key, None)
            self.m.mlx_mouse_hook(self.win, self.on_mouse, None)
            self.m.mlx_hook(self.win, 33, 0, self.on_close, None)
            self.m.mlx_hook(self.win, 12, 1 << 15, self.on_expose, None)
            self.m.mlx_loop_hook(self.mlx_ptr, self.on_loop, None)
            self.m.mlx_loop(self.mlx_ptr)
        finally:
            self.close()

    def close(self) -> None:
        """Elimina immagine, finestra e pointer dalla memoria di MLX.
        Deve essere chiamata alla fine del programma"""
        self.m.mlx_destroy_image(self.mlx_ptr, self.img)
        self.m.mlx_destroy_image(self.mlx_ptr, self.panel)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win)
        self.m.mlx_release(self.mlx_ptr)
