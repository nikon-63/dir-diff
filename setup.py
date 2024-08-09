from setuptools import setup, find_packages

setup(
    name="dir-diff",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dir-diff = dir_diff_tool.dir_diff:main',
        ],
    },
    author="Thomas Nicolson",
    description="Simple tool to compare the contents of two directories",
    url="https://github.com/nikon-63/dir-diff.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
