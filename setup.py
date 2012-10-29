from setuptools import setup, find_packages, Extension
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
# here = os.path.dirname(__file__)
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.3.3'

install_requires = [
    'protobuf',
]

if sys.version_info < (2, 7):
    install_requires += ['unittest2']

# make extensions
def extension_maker():
    extensions = []
    def loop(directory, module=None):
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            name = module + "." + file if module else file
            if os.path.isfile(path) and path.endswith(".c"):
                extensions.append(
                    Extension(
                        name = name[:-2],
                        sources = [path],
                        include_dirs = ['src', "."],
                    )
                )
            elif os.path.isdir(path):
                loop(path, name)
    loop('src/iscool_e', 'iscool_e')
    return extensions

setup(name='iscool_e.pynba',
    version=version,
    description='This is a wsgi middleware to monitor performance in production systems',
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: Log Analysis",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities"
    ],
    keywords='pinba wsgi monitoring',
    author='Xavier Barbosa',
    author_email='xavier.barbosa@iscool-e.com',
    url='https://github.com/IsCoolEntertainment/pynba',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['iscool_e'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=['nose-exclude'],
    ext_modules = extension_maker()
)
