""" module to select search folders.
will traverse all folders and exclude the excluding list"""

from pathlib import Path

def get_folders(folderpath, exclude_list):
    folders = [ d for d in Path(folderpath).glob('**') if d.is_dir]
    return folders