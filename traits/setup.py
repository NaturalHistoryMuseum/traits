from setuptools import setup

setup(
    name='traits',
    version='0.1.0',
    py_modules=['traits'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'yourscript = yourscript:cli',
        ],
    },
)