# Common Issues 

## Error in docTR (Windows)
Some users may encounter an error in docTR
```
Traceback (most recent call last):
  File "C:\CLIPPyX\server.py", line 2, in <module>
    from Index.index_utils import *
  File "C:\CLIPPyX\Index\index_utils.py", line 19, in <module>
    from OCR import apply_OCR
    .
    .
OSError: cannot load library 'gobject-2.0-0': error 0x7e.  Additionally, ctypes.util.find_library() did not manage to locate a library called 'gobject-2.0-0'
```
according to [docTR documentation](https://mindee.github.io/doctr/getting_started/installing.html#prerequisites) you need to install [gtk3-runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) restart your computer and rerun the server.

If the error persists, you can install and OCR python package in modify `OCR.py` to use it

## Error in docTR (macOS)
Some users may encounter an error in docTR

```

WeasyPrint could not import some external libraries. Please carefully follow the installation steps before reporting an issue:
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting 
...
...
OSError: cannot load library 'gobject-2.0-0': dlopen(gobject-2.0-0, 0x0002): tried: 'gobject-2.0-0' (no such file), '/System/Volumes/Preboot/Cryptexes/OSgobject-2.0-0' (no such file), '/Users/usamaahmed/miniconda3/envs/clippyx/bin/../lib/gobject-2.0-0' (no such file), '/usr/lib/gobject-2.0-0' (no such file, not in dyld cache), 'gobject-2.0-0' (no such file), '/usr/local/lib/gobject-2.0-0' (no such file), '/usr/lib/gobject-2.0-0' (no such file, not in dyld cache).  Additionally, ctypes.util.find_library() did not manage to locate a library called 'gobject-2.0-0'
```

To fix this just install weasyprint using `brew`. If you are using conda install it in the environment too.
```
brew install weasyprint
conda install conda-forge::weasyprint
```