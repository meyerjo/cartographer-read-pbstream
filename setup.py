import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pbstream",
    version="0.0.1",
    author="Johannes Meyer",
    author_email="meyerjo@tf.uni-freiburg.de",
    description="Read *.pbstream from cartographer",
    long_description_content_type="text/markdown",
    url="https://github.com/meyerjo/cartographer-read-pbstream",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages("src"),
    python_requires=">=3.6",
    install_requires=[
        'setuptools>42',
    ]
)