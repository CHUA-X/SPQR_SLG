import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SPQR_SLG",
    version="0.0.1",
    author="CHUA某人",
    author_email="chua-x@outlook.com",
    description="SPQR Games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CHUA-X/SPQR_SLG",
    packages=setuptools.find_packages(where='./src'),
    package_dir={"": "src"},
    install_requires=["pygame,networkx,yaml"],
    package_data={
        '': ['.ogg', '.png', '.ttf', '.txt', '.yml', '.cfg'],
    },
    keyword=['Python', 'python', 'SPQR', 'games', 'SLG'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
)
