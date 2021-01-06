import setuptools
from setuptools import setup, find_packages

# with open("readme.md", "r", encoding="utf-8") as fh:
with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pidcmes',
    version='1.0.0',
    description='DC voltage measurement on two GPIO pins',
    author='jo metra',
    author_email='pidcmes@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/josmet52/pidcmes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    platforms='Raspberry PI'
)
