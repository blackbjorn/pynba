from setuptools import setup, find_packages, Extension, Command
import sys
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.4.3'

install_requires = [
    'six'
]

if sys.version_info < (2, 7):
    install_requires += ['unittest2']


def loop(directory, module=None):
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        name = module + "." + file if module else file
        if os.path.isfile(path):
            yield path, name.rpartition('.')[0]
        elif os.path.isdir(path):
            for path2, name2 in loop(path, name):
                yield path2, name2


# make extensions
def extension_maker():
    extensions = []

    for path, name in loop('src/iscool_e', 'iscool_e'):
        if path.endswith(".c"):
            extensions.append(
                Extension(
                    name=name,
                    sources=[path],
                    include_dirs=['src', "."],
                )
            )
    return extensions


class CythonizeCommand(Command):
    description = "cythonize all *.pyx files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from distutils.spawn import find_executable
        import subprocess
        import sys

        errno = 0
        executable = find_executable('cython')
        if not executable:
            print('cython is not installed')
            errno = 1
        else:
            for path, name in loop('src/iscool_e', 'iscool_e'):
                if path.endswith(".pyx"):
                    dest = path.rpartition('.')[0] + '.c'
                    if os.path.exists(dest) and os.path.getmtime(path) <= os.path.getmtime(dest):
                        print('cythonize {} noop'.format(path))
                        continue
                    else:
                        errno = subprocess.call([executable, path])
                        print('cythonize {} ok'.format(path))
                        if errno != 0:
                            print('cythonize {} failed'.format(path))

        if errno != 0:
            raise SystemExit(errno)


setup(
    name='iscool_e.pynba',
    version=version,
    description=str(
        'lightweight timers and wsgi middleware to '
        'monitor performance in production systems'
    ),
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
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
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
    package_dir={'': 'src'},
    namespace_packages=['iscool_e'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=['nose-exclude'],
    ext_modules=extension_maker(),
    cmdclass = {'cythonize': CythonizeCommand},
)
