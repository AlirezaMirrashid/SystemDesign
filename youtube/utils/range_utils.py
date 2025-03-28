# def parse_range_header(range_header, file_size):
#     """
#     Parse the Range header to determine the start and end bytes.
#     Example: "bytes=0-1023"
#     """
#     try:
#         range_val = range_header.strip().split('=')[1]
#         byte_range = range_val.split('-')
#         start = int(byte_range[0]) if byte_range[0] else 0
#         end = int(byte_range[1]) if byte_range[1] else file_size - 1
#         return start, end
#     except:
#         return 0, file_size - 1


def parse_range_header(range_header, file_size):
    """
    Parse the Range header to determine the start and end bytes.
    Example: "bytes=0-1023"
    """
    try:
        range_val = range_header.strip().split('=')[1]
        byte_range = range_val.split('-')
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
        return start, end
    except:
        return 0, file_size - 1
