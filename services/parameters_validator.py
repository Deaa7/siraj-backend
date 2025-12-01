def validate_pagination_parameters(count: int, limit: int) -> tuple[int, int]:
    """
    Validate pagination parameters.

    Args:
        limit: The requested page size.
        count: The requested page number.

    Returns:
        tuple: A tuple of (limit, count) where both values are numbers. If an
        input cannot be converted to a number, defaults are returned instead
        (limit=7 and count=0).
    """
    try:
        validated_limit = int(limit)
    except (TypeError, ValueError):
        validated_limit = 7

    try:
        validated_count = int(count)
    except (TypeError, ValueError):
        validated_count = 0


    if validated_count < 0:
        validated_count = 0
        
    if validated_limit <= 0:
        validated_limit = 7

    if validated_count > 10000000: # 1e7
        validated_count = 0
        
    if validated_limit > 10000000: # 1e7
        validated_limit = 7

    return validated_count,validated_limit 


