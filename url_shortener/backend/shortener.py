# # shortener.py
# import string

# BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

# def encode_base62(num: int) -> str:
    # """Encodes a positive integer into a Base62 string."""
    # if num == 0:
        # return BASE62_CHARS[0]
    
    # encoded = []
    # base = 62
    # while num > 0:
        # num, rem = divmod(num, base)
        # encoded.append(BASE62_CHARS[rem])
    
    # return ''.join(reversed(encoded))


# import string

# BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

# def encode_base62(num: int, length=8) -> str:
    # """Encodes a positive integer into a fixed-length Base62 string (8 characters)."""
    # if num == 0:
        # return BASE62_CHARS[0] * length  # If the counter starts at 0, return "00000000"

    # encoded = []
    # base = 62
    # while num > 0:
        # num, rem = divmod(num, base)
        # encoded.append(BASE62_CHARS[rem])
    
    # short_code = ''.join(reversed(encoded))

    # # Pad with leading '0' if shorter than required length
    # return short_code.rjust(length, BASE62_CHARS[0])


# import string

# BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

# def encode_base62(num: int) -> str:
    # """Encodes a positive integer into a Base62 string."""
    # if num == 0:
        # return BASE62_CHARS[0]

    # encoded = []
    # base = 62
    # while num > 0:
        # num, rem = divmod(num, base)
        # encoded.append(BASE62_CHARS[rem])

    # return ''.join(reversed(encoded))

import string
BASE62_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

def encode_base62(num: int, length=8) -> str:
    """Encodes a positive integer into a Base62 string and pads to a fixed length."""
    encoded = []
    base = 62

    while num > 0:
        num, rem = divmod(num, base)
        encoded.append(BASE62_CHARS[rem])

    # return ''.join(reversed(encoded))
    
    short_code = ''.join(reversed(encoded))
    
    # Ensure the code is always 8 characters long by padding with '0'
    return short_code.rjust(length, '0')
