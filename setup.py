from setuptools import setup,find_packages
from aeromonasanistyper import __version__

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='aeromonasanistyper',
      version=__version__,
      description='assignment of ANI defined species to Aeromonas genomes',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'License :: OSI Approved :: GPLv3',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Medical Science Apps.',
          'Intended Audience :: Science/Research',
      ],
      keywords='genomic taxonomy aeromonas ANI',
      url='https://github.com/lizhanglab/aeromonasanistyper',
      author='Alex Lu',
      author_email='alex.c.lu@unsw.edu.au',
      license='GPLv3',
      packages=find_packages(exclude=['tests', 'docs']),
      include_package_data=True,
      entry_points={
          'console_scripts': ['aeromonasanistyper=aeromonasanistyper.aeromonasanistyper:main'],
      },
      zip_safe=False)