import os
import platform
from setuptools import setup, find_packages, Extension, Command
import sys

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.5.4'

install_requires = [
    'six'
]


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

    if platform.python_implementation() == 'CPython':
        for path, name in loop('pynba', 'pynba'):
            if path.endswith(".c"):
                    extensions.append(
                    Extension(
                        name=name,
                        sources=[path]
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

        exitcode = 0
        errno = 0
        executable = find_executable('cython')
        if not executable:
            print('cython is not installed')
            exitcode = 1
        else:
            for path, name in loop('pynba', 'pynba'):
                if path.endswith(".pyx"):
                    dest = path.rpartition('.')[0] + '.c'
                    if os.path.exists(dest) and os.path.getmtime(path) <= os.path.getmtime(dest):
                        print('cythonize {} noop'.format(path))
                        continue
                    else:
                        errno = subprocess.call([executable, path])
                        print('cythonize {} ok'.format(path))
                        if errno != 0:
                            exitcode = errno
                            print('cythonize {} failed'.format(path))

        if exitcode > 0:
            raise SystemExit(exitcode)


setup(
    name='pynba',
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
    packages=find_packages(),
    keywords='pinba wsgi monitoring',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://github.com/johnnoone/pynba',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    # see https://www.python.org/dev/peps/pep-0426/#environment-markers
    extras_require={
        ':python_version=="2.7"': ['enum34'],
        ':python_version=="3.2"': ['enum34'],
        ':python_version=="3.3"': ['enum34'],
    },
    tests_require=[],
    ext_modules=extension_maker(),
    cmdclass = {'cythonize': CythonizeCommand},
)
