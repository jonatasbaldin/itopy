from distutils.core import setup

setup(
    name="itopy",
    version="0.1.7",
    author="Jonatas Baldin",
    author_email="jonatas.baldin@gmail.com",
    packages=["itopy"],
    keywords="itop api cmdb",
    url="https://github.com/jonatasbaldin/itopy/",
    description="Library for manipulating iTOP CMDB/ITSM",
    install_requires=[
        "requests",
    ],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: System'
    ]
)

