import sys
import os
import shutil
from distutils.core import setup
from distutils.extension import Extension

try:
    have_cython = True
    from Cython.Distutils import build_ext
except:
    have_cython = False

try:
    import numpy
except:
    print '#' * 80
    print
    print 'PyMT require numpy now. Please install it before running PyMT setup'
    print
    print '#' * 80
    sys.exit(1)


# extract version (simulate doc generation, pymt will be not imported)
os.environ['PYMT_DOC_INCLUDE'] = '1'
import pymt

# extracts all examples files except sandbox
examples = []
examples_allowed_ext = ('readme', 'py', 'wav', 'png', 'jpg', 'svg',
                        'avi', 'gif', 'txt', 'ttf', 'obj', 'mtl')
for root, subFolders, files in os.walk('examples'):
    if 'sandbox' in root:
        continue
    for file in files:
        ext = file.split('.')[-1].lower()
        if ext not in examples_allowed_ext:
            continue
        examples.append(os.path.join(root,file))

# modules
numpy_transform_ext = Extension(
    'pymt.c_ext._transformations',
    ['pymt/c_ext/transformations.c'],
    include_dirs=[numpy.get_include()],
    extra_compile_args=[])

ext_modules = [numpy_transform_ext]
cmdclass = {}
if have_cython:
    cmdclass['build_ext'] = build_ext
    libraries = []
    include_dirs = []
    extra_link_args = []
    if sys.platform == 'win32':
        libraries.append('opengl32')
    elif sys.platform == 'darwin':
        # On OSX, gl.h is not in GL/gl.h but OpenGL/gl.h. Cython has no
        # such thing as #ifdef, hence we just copy the file here.
        source = '/System/Library/Frameworks/OpenGL.framework/Versions/A/Headers/gl.h'
        incl = 'build/include/'
        dest = os.path.join(incl, 'GL/')
        try:
            os.makedirs(dest)
        except OSError:
            # Already exists, so don't care
            pass
        shutil.copy(source, dest)
        include_dirs = [incl]
        # On OSX, it's not -lGL, but -framework OpenGL...
        extra_link_args = ['-framework', 'OpenGL']
    else:
        libraries.append('GL')

    ext_modules.append(Extension('pymt.c_ext.c_graphics',
        ['pymt/c_ext/c_graphics.pyx'],
        libraries=libraries,
        include_dirs=include_dirs,
        extra_link_args=extra_link_args))
    ext_modules.append(Extension('pymt.c_ext.c_graphx',
        ['pymt/c_ext/c_graphx.pyx'],
        libraries=libraries,
        include_dirs=include_dirs,
        extra_link_args=extra_link_args))
    ext_modules.append(Extension('pymt.c_ext.c_accelerate',
        ['pymt/c_ext/c_accelerate.pyx']))

# setup !
setup(
    name='PyMT',
    version=pymt.__version__,
    author='PyMT Crew',
    author_email='pymt-dev@googlegroups.com',
    url='http://pymt.eu/',
    license='LGPL',
    description='A framework for making accelerated multitouch UI',
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    packages=[
        'pymt',
        'pymt.c_ext',
        'pymt.core',
        'pymt.core.audio',
        'pymt.core.camera',
        'pymt.core.image',
        'pymt.core.spelling',
        'pymt.core.svg',
        'pymt.core.text',
        'pymt.core.video',
        'pymt.graphics',
        'pymt.graphx',
        'pymt.input',
        'pymt.input.postproc',
        'pymt.input.providers',
        'pymt.lib',
        'pymt.lib.osc',
        'pymt.modules',
        'pymt.tools',
        'pymt.tools.calibration',
        'pymt.tools.designerapp',
        'pymt.ui',
        'pymt.ui.widgets',
        'pymt.ui.widgets.composed',
        'pymt.ui.widgets.layout',
        'pymt.ui.window',
    ],
    package_dir={'pymt': 'pymt'},
    package_data={'pymt': [
        'data/icons/filetype/*.png',
        'data/icons/svg/*.svg',
        'data/icons/*.png',
        'data/*.css',
        'data/*.png',
        'data/*.ttf',
        'tools/designerapp/icons/*.png']
    },
    data_files=[('share/pymt-examples', examples)],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Artistic Software',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: User Interfaces',
    ]
)
