from datetime import datetime
from typing import List, Optional


def normalize(text: str, max_len: int = 6) -> str:
    """Uppercase, keep alnum only, trim to max_len."""
    cleaned = "".join(ch for ch in str(text).upper() if ch.isalnum())
    return cleaned[:max_len] if cleaned else "UNK"


def format_date(date: Optional[str] = None) -> str:
    """
    Return YYYYMMDD.
    Accepts None (today), YYYYMMDD, or YYYY-MM-DD.
    """
    if date is None or str(date).strip() == "":
        return datetime.now().strftime("%Y%m%d")

    date_code = str(date).replace("-", "").strip()
    if len(date_code) != 8 or not date_code.isdigit():
        raise ValueError("date must be YYYYMMDD or YYYY-MM-DD")
    return date_code


def make_plant_id(
    strain: str,
    mother_num: int,
    clone_num: int,
    condition: str,
    fert_rate: str,
    date: Optional[str] = None,
    seq: int = 1
) -> str:
    """
    Format:
    [STRAIN]-M##-C##-[COND]-F[RATE]-YYYYMMDD-##
    Example:
    GG4-M02-C05-IND-F150-20260830-01
    """
    strain_code = normalize(strain, 6)
    cond_code = normalize(condition, 4)
    fert_code = normalize(fert_rate, 5)
    date_code = format_date(date)

    return f"{strain_code}-M{mother_num:02d}-C{clone_num:02d}-{cond_code}-F{fert_code}-{date_code}-{seq:02d}"


def make_batch_ids(
    strain: str,
    mother_num: int,
    start_clone_num: int,
    condition: str,
    fert_rate: str,
    batch_size: int = 10,
    date: Optional[str] = None
) -> List[str]:
    """
    Generate a batch of IDs.
    - clone number increments each item
    - seq increments from 01..batch_size
    """
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    ids = []
    for i in range(batch_size):
        clone_num = start_clone_num + i
        seq = i + 1
        pid = make_plant_id(
            strain=strain,
            mother_num=mother_num,
            clone_num=clone_num,
            condition=condition,
            fert_rate=fert_rate,
            date=date,
            seq=seq,
        )
        ids.append(pid)
    return ids


if __name__ == "__main__":
    # quick demo
    batch = make_batch_ids(
        strain="Gorilla Glue 4",
        mother_num=2,
        start_clone_num=1,
        condition="IND",
        fert_rate="150",
        batch_size=10,
        date=None
    )
    for item in batch:
        print(item)
