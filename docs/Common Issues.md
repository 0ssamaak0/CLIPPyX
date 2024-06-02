# Common Issues 

## Error in docTR if running CLIPPyX server on windows
if running server on windows, some users may encounter an error in docTR
```
Traceback (most recent call last):
  File "C:\testclip\CLIPPyX\server.py", line 2, in <module>
    from Index.index_utils import *
  File "C:\testclip\CLIPPyX\Index\index_utils.py", line 19, in <module>
    from OCR import apply_OCR
    .
    .
OSError: cannot load library 'gobject-2.0-0': error 0x7e.  Additionally, ctypes.util.find_library() did not manage to locate a library called 'gobject-2.0-0'
```
according to [docTR documentation](https://mindee.github.io/doctr/getting_started/installing.html#prerequisites) you need to install [gtk3-runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) restart your computer and rerun the server.

If the error persists, you can install and OCR python package in modify `OCR.py` to use it