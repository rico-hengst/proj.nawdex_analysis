import glob
from nawdex_analysis._version import __version__
from setuptools import setup, find_packages

setup(name='nawdex_analysis',
      version = __version__,
      description = 'Collection of NAWDEX Analysis Tools',
      author = 'Fabian Senf',
      author_email = 'senf@tropos.de',
      license = 'GPL',
      packages = find_packages(),
      scripts = glob.glob('bin/*[!~]'),
      #['bin/coorga_save_cluster_properties', 'bin/coorga_save_interesting_cl],
#['coorga', 'coorga.inout', 'coorga.object_creation', 'coorga.metrics'],
      zip_safe = False)

