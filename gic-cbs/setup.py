from setuptools import setup, find_packages

setup(
    name='gic-cbs',
    version='0.1.0',
    author='Adrien Fort',
    author_email='fort.adrien@gmail.com',
    description='Simple Cinema Booking System',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/gic-cbs',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your project dependencies here
    ],
)