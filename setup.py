# run "python setup.py install" to install
#
# see https://docs.python.org/3/distutils/introduction.html
# or  https://docs.python.org/3/distutils/setupscript.html

from distutils.core import setup
setup(name="prmake",
      version="0.4.2",
      description="make preprocessor",
      author="Peter Ballard",
      author_email="pb@peterballard.org",
      url="https://github.com/peterballard/prmake",
      py_modules=[],
      scripts=["prmake"],
      )
