from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

name = 'multisheller'
version_ns = {}
with open(here / name / '_version.py') as f:
    exec(f.read(), {}, version_ns)

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='multisheller',
    version=version_ns['__version__'],
    description='A python toolbox to generate different shell scripts quickly',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wolfv/multisheller',
    author='Wolf Vollprecht, QuantStack',
    author_email='wolf.vollprecht@quantstack.net',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=find_packages(),
    python_requires='>=3.6, <4',
    extras_require={  # Optional
        'dev': [],
        'test': ['pytest'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/wolfv/multisheller/issues',
        'Source': 'https://github.com/wolfv/multisheller/',
    },
)
