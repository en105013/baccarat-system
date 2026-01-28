
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

ROWS = 6

@dataclass
class Cell:
    v: str
    ties: int = 0

def bead_road(results: List[str], max_cols: int) -> List[List[Optional[str]]]:
    grid = [[None for _ in range(max_cols)] for _ in range(ROWS)]
    for i, r in enumerate(results[:ROWS*max_cols]):
        grid[i % ROWS][i // ROWS] = r
    return grid

def col_height(big: Dict[Tuple[int,int], Cell], col: int) -> int:
    h=0
    for r in range(ROWS):
        if (col,r) in big:
            h=r+1
    return h

def exists(big: Dict[Tuple[int,int], Cell], col: int, row: int) -> bool:
    return (col,row) in big

def _derived_color(big: Dict[Tuple[int,int], Cell], col:int, row:int, back:int) -> Optional[str]:
    # back: BigEye=1, Small=2, Cockroach=3
    if row == 0:
        # new column head: compare previous column height vs (previous-back) column height
        left = col-1
        other = col-1-back
        if other < 0:
            return None
        return "R" if col_height(big, left) == col_height(big, other) else "U"
    else:
        # continuing down/right: compare existence of (col-back, row)
        ref = col-back
        if ref < 0:
            return None
        return "R" if exists(big, ref, row) else "U"

def _place_seq_cell(grid: Dict[Tuple[int,int], str], color: str, max_cols:int) -> None:
    # place like a "road": same color goes down, else new column
    if not grid:
        grid[(0,0)] = color
        return
    # find last placed position by max (col,row) in insertion order not stored; approximate by tracking in caller
    raise RuntimeError("caller must provide placement order")

def compute_all(results: List[str], bead_cols:int=40, big_cols:int=40, small_cols:int=20):
    bead = bead_road(results, bead_cols)

    big: Dict[Tuple[int,int], Cell] = {}
    bigeye: Dict[Tuple[int,int], str] = {}
    small: Dict[Tuple[int,int], str] = {}
    cockroach: Dict[Tuple[int,int], str] = {}

    # Track last placement for each derived road to keep correct insertion order
    last_d = {"bigeye": None, "small": None, "cockroach": None}  # (col,row)
    last_c = {"bigeye": None, "small": None, "cockroach": None}  # color

    def place_derived(name: str, color: str):
        grid = {"bigeye": bigeye, "small": small, "cockroach": cockroach}[name]
        lp = last_d[name]
        lc = last_c[name]
        if lp is None:
            grid[(0,0)] = color
            last_d[name] = (0,0)
            last_c[name] = color
            return
        c,r = lp
        if color == lc:
            # try go down
            if r+1 < ROWS and (c, r+1) not in grid:
                np = (c, r+1)
            else:
                np = (c+1, r)
        else:
            np = (c+1, 0)
        tc,tr = np
        while (tc,tr) in grid:
            tc += 1
        if tc >= small_cols:
            return
        grid[(tc,tr)] = color
        last_d[name] = (tc,tr)
        last_c[name] = color

    last_pos: Optional[Tuple[int,int]] = None
    last_bp: Optional[str] = None

    def occ(c:int,r:int)->bool:
        return (c,r) in big

    for x in results:
        if x == "T":
            if last_pos is not None:
                big[last_pos].ties += 1
            continue
        if x not in ("B","P"):
            continue

        if last_bp is None:
            last_pos = (0,0)
            big[last_pos] = Cell(v=x, ties=0)
            last_bp = x
            continue

        c,r = last_pos  # type: ignore
        if x == last_bp:
            if r+1 < ROWS and not occ(c, r+1):
                pos = (c, r+1)
            else:
                pos = (c+1, r)
        else:
            pos = (c+1, 0)

        tc,tr = pos
        while occ(tc,tr):
            tc += 1
        if tc >= big_cols:
            break

        # Determine derived colors based on the position we're about to place (using current big state)
        # Only generate if rules allow (None means "not started yet")
        be = _derived_color(big, tc, tr, back=1)
        sm = _derived_color(big, tc, tr, back=2)
        co = _derived_color(big, tc, tr, back=3)
        if be: place_derived("bigeye", be)
        if sm: place_derived("small", sm)
        if co: place_derived("cockroach", co)

        # Place big road cell
        last_pos = (tc,tr)
        big[last_pos] = Cell(v=x, ties=0)
        last_bp = x

    return {
        "bead": bead,
        "big": big,
        "bigeye": bigeye,
        "small": small,
        "cockroach": cockroach,
        "bead_cols": bead_cols,
        "big_cols": big_cols,
        "small_cols": small_cols,
    }
