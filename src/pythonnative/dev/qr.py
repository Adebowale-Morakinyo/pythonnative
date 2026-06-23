"""A tiny, dependency-free QR encoder for ``pn start``.

``pn start`` prints a scannable QR code of the dev-server URL so the
PythonNative Go app can connect by pointing the camera at the terminal. This
module implements just enough of the QR spec to encode a short URL: byte mode,
error-correction level L, versions 1-4 (up to ~78 bytes), single error-block.
That comfortably covers any LAN URL like ``http://192.168.1.20:8765``.

The matrix construction follows Nayuki's public-domain QR Code generator
algorithm. Output is rendered with ANSI background colors so the code is true
black-on-white regardless of terminal theme, which scanners read reliably.

Everything is best-effort: callers wrap [`render_qr`][pythonnative.dev.qr.render_qr]
and fall back to printing the raw URL if anything goes wrong (for example a URL
longer than version 4 can hold).
"""

from __future__ import annotations

from typing import List, Optional

# Data codewords and EC codewords for versions 1-4 at error-correction
# level L (each is a single error-correction block, which is why the
# encoder can skip the general interleaving logic).
_DATA_CODEWORDS = {1: 19, 2: 34, 3: 55, 4: 80}
_ECC_CODEWORDS = {1: 7, 2: 10, 3: 15, 4: 20}
_FORMAT_BITS_L = 1  # 2-bit EC level indicator for level L.

# GF(256) tables (primitive polynomial 0x11d), built once at import.
_GF_EXP = [0] * 512
_GF_LOG = [0] * 256


def _init_tables() -> None:
    value = 1
    for i in range(255):
        _GF_EXP[i] = value
        _GF_LOG[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        _GF_EXP[i] = _GF_EXP[i - 255]


_init_tables()


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _GF_EXP[_GF_LOG[a] + _GF_LOG[b]]


def _rs_generator(degree: int) -> List[int]:
    poly = [1]
    for i in range(degree):
        # Multiply poly by (x - alpha^i).
        new = [0] * (len(poly) + 1)
        for j, coeff in enumerate(poly):
            new[j] ^= _gf_mul(coeff, 1)
            new[j + 1] ^= _gf_mul(coeff, _GF_EXP[i])
        poly = new
    return poly


def _rs_ecc(data: List[int], degree: int) -> List[int]:
    gen = _rs_generator(degree)
    remainder = [0] * degree
    for byte in data:
        factor = byte ^ remainder[0]
        remainder = remainder[1:] + [0]
        for i in range(degree):
            remainder[i] ^= _gf_mul(gen[i + 1], factor)
    return remainder


def _pick_version(num_bytes: int) -> int:
    for version in (1, 2, 3, 4):
        # 4-bit mode + 8-bit count + 4-bit terminator = 16 bits overhead.
        capacity_bits = _DATA_CODEWORDS[version] * 8
        if 4 + 8 + num_bytes * 8 + 4 <= capacity_bits:
            return version
    raise ValueError("data too long for a level-L version 1-4 QR code")


def _encode_data(payload: bytes, version: int) -> List[int]:
    bits: List[int] = []

    def push(value: int, length: int) -> None:
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)

    push(0b0100, 4)  # Byte mode.
    push(len(payload), 8)  # Character count (8 bits for versions 1-9).
    for byte in payload:
        push(byte, 8)

    capacity_bits = _DATA_CODEWORDS[version] * 8
    push(0, min(4, capacity_bits - len(bits)))  # Terminator.
    while len(bits) % 8 != 0:
        bits.append(0)

    codewords = [int("".join(str(b) for b in bits[i : i + 8]), 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    i = 0
    while len(codewords) < _DATA_CODEWORDS[version]:
        codewords.append(pad[i % 2])
        i += 1
    return codewords


def _alignment_positions(version: int) -> List[int]:
    if version == 1:
        return []
    size = version * 4 + 17
    return [6, size - 7]


def qr_matrix(data: str) -> List[List[bool]]:
    """Encode ``data`` as a QR module matrix.

    Args:
        data: The text to encode (typically a short URL). Encoded as UTF-8
            byte mode.

    Returns:
        A square matrix of booleans where ``True`` means a dark module.

    Raises:
        ValueError: If ``data`` is too long to fit a level-L version 1-4
            code.
    """
    payload = data.encode("utf-8")
    version = _pick_version(len(payload))
    size = version * 4 + 17

    data_cw = _encode_data(payload, version)
    ecc = _rs_ecc(data_cw, _ECC_CODEWORDS[version])
    all_cw = data_cw + ecc

    modules = [[False] * size for _ in range(size)]
    is_function = [[False] * size for _ in range(size)]

    def set_fn(col: int, row: int, dark: bool) -> None:
        modules[row][col] = dark
        is_function[row][col] = True

    def draw_finder(cx: int, cy: int) -> None:
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < size and 0 <= yy < size:
                    dist = max(abs(dx), abs(dy))
                    set_fn(xx, yy, dist not in (2, 4))

    for i in range(size):
        set_fn(6, i, i % 2 == 0)
        set_fn(i, 6, i % 2 == 0)

    draw_finder(3, 3)
    draw_finder(size - 4, 3)
    draw_finder(3, size - 4)

    aligns = _alignment_positions(version)
    skip = {(0, 0), (0, len(aligns) - 1), (len(aligns) - 1, 0)}
    for i, ax in enumerate(aligns):
        for j, ay in enumerate(aligns):
            if (i, j) in skip:
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    set_fn(ax + dx, ay + dy, max(abs(dx), abs(dy)) != 1)

    set_fn(8, size - 8, True)  # Dark module.

    # Reserve the format-information areas (filled after masking).
    for i in range(9):
        if i != 6:
            set_fn(8, i, False)
            set_fn(i, 8, False)
    for i in range(8):
        set_fn(8, size - 1 - i, False)
        set_fn(size - 1 - i, 8, False)

    # Place data + ECC bits in the standard zigzag, skipping function modules.
    bit_index = 0
    total_bits = len(all_cw) * 8
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        for vert in range(size):
            for c in (col, col - 1):
                upward = ((col + 1) & 2) == 0
                row = (size - 1 - vert) if upward else vert
                if not is_function[row][c] and bit_index < total_bits:
                    byte = all_cw[bit_index >> 3]
                    modules[row][c] = ((byte >> (7 - (bit_index & 7))) & 1) != 0
                    bit_index += 1
        col -= 2

    best = _apply_best_mask(modules, is_function, size)
    return best


def _mask_condition(mask: int, row: int, col: int) -> bool:
    if mask == 0:
        return (row + col) % 2 == 0
    if mask == 1:
        return row % 2 == 0
    if mask == 2:
        return col % 3 == 0
    if mask == 3:
        return (row + col) % 3 == 0
    if mask == 4:
        return (row // 2 + col // 3) % 2 == 0
    if mask == 5:
        return (row * col) % 2 + (row * col) % 3 == 0
    if mask == 6:
        return ((row * col) % 2 + (row * col) % 3) % 2 == 0
    return ((row + col) % 2 + (row * col) % 3) % 2 == 0


def _format_bits(mask: int) -> int:
    data = (_FORMAT_BITS_L << 3) | mask
    rem = data
    for _ in range(10):
        rem = (rem << 1) ^ ((rem >> 9) * 0x537)
    return ((data << 10) | rem) ^ 0x5412


def _draw_format(modules: List[List[bool]], size: int, mask: int) -> None:
    bits = _format_bits(mask)

    def bit(i: int) -> bool:
        return ((bits >> i) & 1) != 0

    for i in range(6):
        modules[i][8] = bit(i)
    modules[7][8] = bit(6)
    modules[8][8] = bit(7)
    modules[8][7] = bit(8)
    for i in range(9, 15):
        modules[8][14 - i] = bit(i)

    for i in range(8):
        modules[size - 1 - i][8] = bit(i)
    for i in range(8, 15):
        modules[8][size - 15 + i] = bit(i)
    modules[size - 8][8] = True


def _apply_best_mask(
    modules: List[List[bool]],
    is_function: List[List[bool]],
    size: int,
) -> List[List[bool]]:
    best_matrix: Optional[List[List[bool]]] = None
    best_penalty = -1
    for mask in range(8):
        candidate = [row[:] for row in modules]
        for r in range(size):
            for c in range(size):
                if not is_function[r][c] and _mask_condition(mask, r, c):
                    candidate[r][c] = not candidate[r][c]
        _draw_format(candidate, size, mask)
        penalty = _penalty(candidate, size)
        if best_penalty < 0 or penalty < best_penalty:
            best_penalty = penalty
            best_matrix = candidate
    assert best_matrix is not None
    return best_matrix


def _penalty(matrix: List[List[bool]], size: int) -> int:
    score = 0
    # Rule 1: runs of five or more same-colored modules.
    for line in (matrix, [[matrix[r][c] for r in range(size)] for c in range(size)]):
        for row in line:
            run = 1
            for i in range(1, size):
                if row[i] == row[i - 1]:
                    run += 1
                else:
                    if run >= 5:
                        score += 3 + (run - 5)
                    run = 1
            if run >= 5:
                score += 3 + (run - 5)
    # Rule 2: 2x2 blocks of the same color.
    for r in range(size - 1):
        for c in range(size - 1):
            v = matrix[r][c]
            if v == matrix[r][c + 1] == matrix[r + 1][c] == matrix[r + 1][c + 1]:
                score += 3
    # Rule 3: finder-like 1:1:3:1:1 patterns.
    pattern_a = [True, False, True, True, True, False, True, False, False, False, False]
    pattern_b = list(reversed(pattern_a))
    for line in (matrix, [[matrix[r][c] for r in range(size)] for c in range(size)]):
        for row in line:
            for i in range(size - 11 + 1):
                window = row[i : i + 11]
                if window == pattern_a or window == pattern_b:
                    score += 40
    # Rule 4: overall dark/light balance.
    dark = sum(1 for row in matrix for cell in row if cell)
    total = size * size
    ratio = dark * 100 // total
    score += 10 * (abs(ratio - 50) // 5)
    return score


def render_terminal(matrix: List[List[bool]], *, quiet: int = 2) -> str:
    """Render a module matrix as an ANSI black-on-white QR for the terminal.

    Args:
        matrix: A matrix from [`qr_matrix`][pythonnative.dev.qr.qr_matrix].
        quiet: Width of the white quiet zone around the code, in modules.

    Returns:
        A multi-line string using ANSI background colors (two spaces per
        module) that scans reliably regardless of terminal theme.
    """
    white = "\x1b[107m  \x1b[0m"
    black = "\x1b[40m  \x1b[0m"
    size = len(matrix)
    padded = size + quiet * 2
    lines: List[str] = []
    blank = white * padded
    for _ in range(quiet):
        lines.append(blank)
    for row in matrix:
        cells = [white] * quiet + [black if cell else white for cell in row] + [white] * quiet
        lines.append("".join(cells))
    for _ in range(quiet):
        lines.append(blank)
    return "\n".join(lines)


def render_qr(data: str) -> Optional[str]:
    """Return a terminal QR for ``data``, or ``None`` if it can't be encoded.

    Args:
        data: The text (URL) to encode.

    Returns:
        A renderable multi-line string, or ``None`` when ``data`` is too
        long or encoding fails, so callers can degrade to printing the URL.
    """
    try:
        return render_terminal(qr_matrix(data))
    except Exception:
        return None
