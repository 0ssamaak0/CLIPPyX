import setuptools
from os import path
import pkg_resources

# Check if torch or torchvision is already installed
installed_packages = {pkg.key for pkg in pkg_resources.working_set}
skip_packages = {"torch", "torchvision"}

with open("requirements.txt", "r") as f:
    requirements = []
    for line in f:
        # Split on semicolon to handle any environment markers
        package = line.split(";")[0].strip()
        if package.split("==")[0].lower() not in skip_packages:
            requirements.append(line)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="CLIPPyX",
    version="0.1",
    author="0ssamaak0",
    author_email="0ssamaak0@gmail.com",
    description="CLIPPyX provides an OS-wide image search that supports semantic search in both image content and text on images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0ssamaak0/CLIPPyX",
    python_requires=">=3.11",
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
