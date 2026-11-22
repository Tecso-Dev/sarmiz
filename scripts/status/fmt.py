"""Small formatting helpers shared by the page and the issue renderers: Persian digits, Jalali dates, text bars."""
import datetime as dt

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
JALALI_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                 "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fa_digits(value) -> str:
    return str(value).translate(FA_DIGITS)


def to_jalali(day: dt.date):
    """Gregorian date to (year, month, day) in the Jalali (Persian) calendar."""
    gy, gm, gd = day.year, day.month, day.day
    cumulative = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + cumulative[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def date_fa(day: dt.date) -> str:
    _, jm, jd = to_jalali(day)
    return f"{fa_digits(jd)} {JALALI_MONTHS[jm - 1]}"


def date_en(day: dt.date) -> str:
    return f"{day.day} {EN_MONTHS[day.month - 1]}"


def bar(done: int, total: int, width: int = 10) -> str:
    """Text progress bar for the pinned issue."""
    filled = round(width * done / total) if total else 0
    return "▰" * filled + "▱" * (width - filled)


def percent(done: int, total: int) -> int:
    return int(done * 100 / total) if total else 0
