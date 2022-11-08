'''
Copyright 1999 Illinois Institute of Technology

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL ILLINOIS INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name of Illinois Institute
of Technology shall not be used in advertising or otherwise to promote
the sale, use or other dealings in this Software without prior written
authorization from Illinois Institute of Technology.
'''

from setuptools import setup, find_packages
from codecs import open
from os import path

fpath = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(fpath, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chiplot-analyze',
    version='0.9.8',
    description='A general purpose GUI application used to analyze chiplots.',
    long_description=long_description,
    url='https://github.com/biocatiit/Chiplot-analyze',
    author='BioCAT',
    author_email='biocat@lethocerus.biol.iit.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Intended Audience :: Developers',
        # 'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 3',
    ],
    keywords='chiplot analyze',
    # project_urls={},
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['matplotlib'],
    package_data={
        'chiplot_analyze.sample': ['*.chi*'],
    },
    entry_points={
        'console_scripts': [
            'chiplot-analyze=chiplot_analyze.chiplot_analyze:main',
        ],
    },
)














