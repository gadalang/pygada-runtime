# type: ignore
"""Setup script."""
import io
from setuptools import find_packages, setup


def readme():
    """Return the content of README.md."""
    with open("README.md", "r") as f:
        return f.read()


def read(*filenames, **kwargs):
    """Read contents of multiple files and join them together."""
    encoding: str = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


pkg_info = {}
exec(read("pygada_runtime/__version__.py"), pkg_info)


setup(
    name="pygada_runtime",
    version=pkg_info["__version__"],
    author=pkg_info["__author__"],
    author_email=pkg_info["__author_email__"],
    url=pkg_info["__url__"],
    project_urls={
        "Bug Tracker": "https://github.com/gadalang/pygada-runtime/issues",
        "Source Code": "https://github.com/gadalang/pygada-runtime/",
    },
    description="Python runtime for gada nodes",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    install_requires=["pyyaml", "antlr4-python3-runtime==4.10"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
