try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="smbus2_bmp180",
    version="0.1.0",
    description="Python library to read from  BMP085/BMP180 on a Raspberry Pi using smbus2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: System :: Hardware",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
    ],
    keywords="bmp085 bmp180 raspberry pi",
    url="https://github.com/gmambro/python-bmp180",
    author="Gabriele Mambrini",
    license="Apache",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["smbus2_bmp180"],
    install_requires=[
        "smbus2",
    ],
    scripts=[],
    zip_safe=False,
)
