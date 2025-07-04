from setuptools import setup, find_packages

setup(
    name='tm1637_lgpio',
    version='0.1.0',
    description='TM1637 7-segment LED driver using lgpio on Raspberry Pi',
    author='Domenico Guerra',
    author_email='domenico.guerra.63@gmail.com',
    url='https://github.com/melomane63/tm1637_lgpio',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'lgpio',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Embedded Systems',
    ],
    python_requires='>=3.11',
)
