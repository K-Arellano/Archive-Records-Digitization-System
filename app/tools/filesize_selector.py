def filesize_format(filesize):
    if filesize >= 1024 * 1024 * 1024:  # Greater than or equal to 1 GB
        formatted_size = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
    elif filesize >= 1024 * 1024:  # Greater than or equal to 1 MB
        formatted_size = f"{filesize / (1024 * 1024):.2f} MB"
    else:
        formatted_size = f"{filesize / 1024:.2f} KB"
    
    return formatted_size