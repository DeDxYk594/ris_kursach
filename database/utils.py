import datetime


def prepare_datetime(dt: datetime.datetime) -> str:
    """Форматирует datetime в строку, подходящую для MySQL"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
