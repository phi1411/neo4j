import re
import unicodedata

from app.errors import APIError


def shape_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,31}", value.strip().upper()):
        raise APIError("INVALID_SHAPE_ID", "ID hình không hợp lệ.")
    return value.strip().upper()


def integer(value, field, minimum, maximum):
    if isinstance(value, bool) or not (isinstance(value, int) or (isinstance(value, str) and len(value) <= 3 and re.fullmatch(r"[0-9]+", value))):
        raise APIError("INVALID_PARAMETER", f"Tham số {field} phải là số nguyên từ {minimum} đến {maximum}.")
    number = int(value)
    if not minimum <= number <= maximum:
        raise APIError("INVALID_PARAMETER", f"Tham số {field} phải nằm trong khoảng {minimum}–{maximum}.")
    return number


def normalize_search(value):
    if not isinstance(value, str) or len(value) > 200:
        raise APIError("INVALID_SEARCH", "Từ khóa tìm kiếm phải là chuỗi tối đa 200 ký tự.")
    decomposed = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    normalized = " ".join("".join(ch for ch in decomposed if not unicodedata.combining(ch)).split())
    if not normalized:
        raise APIError("EMPTY_SEARCH", "Vui lòng nhập từ khóa tìm kiếm.")
    return normalized
