
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

ROWS = 6

@dataclass
class Cell:
    v: str
    ties: int = 0

def bead_road(results: List[str], max_cols: int) -> List[List[Optional[str]]]:
    grid = [[None for _ in range(max_cols)] for _ in range(ROWS)]
    for i, r in enumerate(results[:ROWS * max_cols]):
        grid[i % ROWS][i // ROWS] = r
    return grid

def big_road(results: List[str], max_cols: int) -> Dict[Tuple[int, int], Cell]:
    grid: Dict[Tuple[int, int], Cell] = {}
    last_pos: Optional[Tuple[int, int]] = None
    last_bp: Optional[str] = None

    def occ(c: int, r: int) -> bool:
        return (c, r) in grid

    for x in results:
        if x == "T":
            if last_pos is not None:
                grid[last_pos].ties += 1
            continue
        if x not in ("B", "P"):
            continue

        if last_bp is None:
            last_pos = (0, 0)
            grid[last_pos] = Cell(v=x, ties=0)
            last_bp = x
            continue

        c, r = last_pos  # type: ignore
        if x == last_bp:
            if r + 1 < ROWS and not occ(c, r + 1):
                pos = (c, r + 1)
            else:
                pos = (c + 1, r)
        else:
            pos = (c + 1, 0)

        tc, tr = pos
        while occ(tc, tr):
            tc += 1
        if tc >= max_cols:
            break

        last_pos = (tc, tr)
        grid[last_pos] = Cell(v=x, ties=0)
        last_bp = x

    return grid

def compute_all(results: List[str], bead_cols: int = 40, big_cols: int = 40):
    bead = bead_road(results, bead_cols)
    big = big_road(results, big_cols)
    return {"bead": bead, "big": big, "bead_cols": bead_cols, "big_cols": big_cols}
