from setuptools import setup

setup(name='pyTestsDHCP',
      version='0.1',
      description="My sample package",
      long_description="",
      author='Igor Rymaruk',
      author_email='rymaruk@gmail.com',
      license='MIT',
      packages=['pyTestsDHCP'],
      zip_safe=False,
      install_requires=[
          'pytest',
          'Sphinx',
          ],
      )