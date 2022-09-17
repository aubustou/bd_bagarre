from setuptools import setup

setup(
    name="bd_bagarre",
    version="0.1",
    packages=["bd_bagarre", "bd_bagarre.model"],
    url="",
    license="MIT",
    author="Aubustou",
    author_email="",
    description="",
    install_requires=[
        "sqlalchemy",
        "apischema",
        "lxml",
        "feedgenerator",
    ],
    extras_require={
        "dev": [
            "pytest",
            "xmltodict",
        ],
    },
)
