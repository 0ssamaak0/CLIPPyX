import setuptools
import subprocess
import platform
from os import path

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

try:
    import torch
    import torchvision
except ImportError:
    # check if platform isn't darwn
    if platform.system() != "Darwin":
        subprocess.run(["pip", "install", "torch", "torchvision"])
    else:
        subprocess.run(
            [
                "pip",
                "install",
                "torch",
                "torchvision",
                "--index-url https://download.pytorch.org/whl/cu118",
            ]
        )


setuptools.setup(
    name="CLIPPyX",
    version="0.1",
    author="0ssamaak0",
    author_email="0ssamaak0@gmail.com",
    description="CLIPPyX provides an OS-wide image search that supports semantic search in both image content and text on images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0ssamaak0/CLIPPyX",
    python_requires=">=3.10",
    install_requires=requirements,
    packages=setuptools.find_packages(
        exclude=[
            "db",
            "checkpoints",
            "Everything-SDK",
            "images",
            "ml-mobileclip",
            "CLIPPyX.egg-info/",
        ]
    ),
    entry_points={"console_scripts": ["CLIPPyX=main"]},
)
# pip install git+https://github.com/apple/ml-mobileclip.git@main#egg=mobileclip --no-deps
