def round_float(number: float) -> float:
    return float(f'{number:.2f}')


def format_float_input_string(number: str) -> float:
    number = number.replace(',', '.')
    number = number.replace(' ', '')
    try:
        return float(number)
    except ValueError as e:
        raise e
