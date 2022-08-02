"""Support code for lane line detection"""
# Standard Imports

# Third Party Imports

# Local Imports

def check_lane_side(
    slope: float,
    intercept: float,
    n_row: int,
    n_col: int
):
    """Check whether lane line is a left lane line or right lane line

    Args:
        slope: Line slope
        intercept: Line intercept
        n_row: Number of image rows
        n_col: Number of image columns

    Returns:
        line_type: 'left' or 'right'
    """
    # Find x for where y = (bottom image) = slope * x + intercept
    x_bottom = (n_row - intercept) / slope
    line_side = 'left' if x_bottom < (n_col / 2) else 'right'
    return line_side
