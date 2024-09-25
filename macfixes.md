```

WeasyPrint could not import some external libraries. Please carefully follow the installation steps before reporting an issue:
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting 

-----

Traceback (most recent call last):
  File "/Users/usamaahmed/Documents/Projects/CLIPPyX/server.py", line 3, in <module>
    from Index.index_utils import *
  File "/Users/usamaahmed/Documents/Projects/CLIPPyX/Index/index_utils.py", line 22, in <module>
    from OCR import apply_OCR
  File "/Users/usamaahmed/Documents/Projects/CLIPPyX/OCR.py", line 2, in <module>
    from doctr.models import ocr_predictor
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/doctr/__init__.py", line 1, in <module>
    from . import io, models, datasets, transforms, utils
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/doctr/io/__init__.py", line 2, in <module>
    from .html import *
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/doctr/io/html.py", line 8, in <module>
    from weasyprint import HTML
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/weasyprint/__init__.py", line 419, in <module>
    from .css import preprocess_stylesheet  # noqa: I001, E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/weasyprint/css/__init__.py", line 28, in <module>
    from .computed_values import COMPUTER_FUNCTIONS
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/weasyprint/css/computed_values.py", line 9, in <module>
    from ..text.ffi import ffi, pango, units_to_double
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/weasyprint/text/ffi.py", line 431, in <module>
    gobject = _dlopen(
              ^^^^^^^^
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/weasyprint/text/ffi.py", line 420, in _dlopen
    return ffi.dlopen(names[0])  # pragma: no cover
           ^^^^^^^^^^^^^^^^^^^^
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/cffi/api.py", line 150, in dlopen
    lib, function_cache = _make_ffi_library(self, name, flags)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/cffi/api.py", line 832, in _make_ffi_library
    backendlib = _load_backend_lib(backend, libname, flags)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/usamaahmed/miniconda3/envs/clippyx/lib/python3.12/site-packages/cffi/api.py", line 827, in _load_backend_lib
    raise OSError(msg)
OSError: cannot load library 'gobject-2.0-0': dlopen(gobject-2.0-0, 0x0002): tried: 'gobject-2.0-0' (no such file), '/System/Volumes/Preboot/Cryptexes/OSgobject-2.0-0' (no such file), '/Users/usamaahmed/miniconda3/envs/clippyx/bin/../lib/gobject-2.0-0' (no such file), '/usr/lib/gobject-2.0-0' (no such file, not in dyld cache), 'gobject-2.0-0' (no such file), '/usr/local/lib/gobject-2.0-0' (no such file), '/usr/lib/gobject-2.0-0' (no such file, not in dyld cache).  Additionally, ctypes.util.find_library() did not manage to locate a library called 'gobject-2.0-0'
```

Fix
```
brew install weasyprint
conda install conda-forge::weasyprint
```