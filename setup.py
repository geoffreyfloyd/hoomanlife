from distutils.core import setup

VERSION = '0.1.0'
desc    = """Personal projects and tasks management system."""

setup(name='_hoomanlife',
        version=VERSION, 
        author='Geoffrey Floyd',
        author_email='geoffrey.floyd@hoomanlogic.com',
        url='http://github.com/hoomanlogic/_hoomanlife/',
        download_url='https://pypi.python.org/pypi/_hoomanlife/',
        description='Personal projects and tasks management system.',
        license='http://www.apache.org/licenses/LICENSE-2.0',
        packages=['_hoomanlife'],
        py_modules=['hoomanlife'],
        platforms=['Any'],
        long_description=desc,
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Apache Software License',
                     'Operating System :: OS Independent',
                     'Topic :: Text Processing',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                    ]
        )