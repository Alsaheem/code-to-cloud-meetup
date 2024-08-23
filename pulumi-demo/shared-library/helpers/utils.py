
def is_valid_bucket_name(bucket_name: str) -> bool:
    """Checks if the provided bucket name is valid according to S3 naming conventions."""
    if bucket_name.islower():
        return True
    else:
        return False