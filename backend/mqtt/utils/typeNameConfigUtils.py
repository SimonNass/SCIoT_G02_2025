import logging

def get_simple_default_middle_values(max_value: float, min_value: float) -> tuple[float, float]:
    """
    Create default middle values for a device type configuration.
    
    Args:
        max_value (float): The maximum value for the device type.
        min_value (float): The minimum value for the device type.
    
    Returns:
        tuple: A tuple containing the lower and upper mid limits.
    """
    if max_value is None or min_value is None:
        return None, None
    if max_value <= min_value:
        logging.error("Max value must be greater than min value")
        return None, None
    
    lower_mid_limit = min_value + (max_value - min_value) / 3
    upper_mid_limit = max_value - (max_value - min_value) / 3
    
    return lower_mid_limit, upper_mid_limit
 