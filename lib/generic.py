
def rescale(x, original_range: tuple[float, float], new_range: tuple[float, float]) -> float:
    """
    Linearly rescale a value from one range to another range.

    Parameters:
    - x: The value to rescale.
    - original_range: A tuple (A, B) representing the original range.
    - new_range: A tuple (C, D) representing the new range.

    Returns:
    - The rescaled value.
    """
    A, B = original_range
    C, D = new_range
    return C + (x - A) * (D - C) / (B - A)
