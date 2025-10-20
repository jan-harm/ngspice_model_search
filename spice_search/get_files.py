""" file searcher"""


from pathlib import Path

def getFiles(folder_paths):
    """Searches all files for each path, filters on extensions when any is given
    folders dict {index: folder, filecount, modelcount}
    files dict { index: [path, modelcount, boolean]}
    extensions { index: [ext, count, boolean]"""

    all_files = {}
    file_index = 0
    extensions = dict()

    for index,v in folder_paths.items():
        p = Path(v[0])
        if p.exists():
            files = [x for x in p.iterdir() if not x.is_dir()]
            folder_paths[index][1] = len(files)
            for f in files:
                file_index += 1
                all_files[file_index] = [str(f), 0, True]
                extensions[str(f.suffix)] = extensions.get(str(f.suffix), 0) + 1
    ext_index = 0
    extensions_list = {}
    for k, v in extensions.items():
        ext_index += 1
        extensions_list[ext_index] = [k, v, True]

    return all_files, extensions_list
