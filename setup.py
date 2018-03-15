from distutils.core import setup

setup(
    name="itopy",
    version="0.1.3",
    author="Jonatas Baldin",
    author_email="jonatas.baldin@gmail.com",
    packages=["itopy"],
    keywords="itop api cmdb",
    url="https://github.com/jonatasbaldin/itopy/",
    description="Library for manipulating iTOP CMDB/ITSM",
    long_description=open('README.md').read(),
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

