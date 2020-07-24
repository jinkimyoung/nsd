from setuptools import setup, find_packages

setup(
    name                = 'nds',
    version             = '0.1',
    description         = 'nds',
    author              = 'k.jin',
    author_email        = 'gjinki@gmail.com',
    url                 = 'https://github.com/jeakwon/ccpy',
    download_url        = 'https://github.com/jeakwon/ccpy/archive/0.0.tar.gz',
    install_requires    =  [],
    packages            = find_packages(exclude = []),
    keywords            = ['ccpy'],
    python_requires     = '>=3',
    package_data        = {},
    zip_safe            = False,
    classifiers         = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)