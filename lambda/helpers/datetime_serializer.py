from datetime import datetime

def serialize_datetime(obj):
    """Helper function to convert datetime objects to string.

    Args:
        obj: The object to serialize.

    Returns:
        str: ISO formatted string if obj is a datetime, else raises TypeError.

    Raises:
        TypeError: If obj is not serializable.
    """

    # Check if the object is an instance of datetime
    if isinstance(obj, datetime):

        # Return the ISO format of the datetime object
        return obj.isoformat()

    # If the object is not a datetime, raise TypeError
    raise TypeError("Type not serializable")
