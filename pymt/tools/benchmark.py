'''
Benchmark for PyMT Framework
'''

benchmark_version = '1'

import pymt
import sys
import os
import OpenGL
import time
from OpenGL.GL import *
from random import randint, random
from pymt import *
from time import clock

try:
    window_size = getWindow().size
except:
    window_size = MTWindow().size

class bench_core_label:
    '''Core: label creation (10000 * 10 a-z)'''
    def __init__(self):
        labels = []
        for x in xrange(10000):
            label = map(lambda x: chr(randint(ord('a'), ord('z'))), xrange(10))
            labels.append(''.join(label))
        self.labels = labels
    def run(self):
        o = []
        for x in self.labels:
            o.append(Label(label=x))


class bench_widget_creation:
    '''Widget: creation (10000 MTWidget)'''
    def run(self):
        o = []
        for x in xrange(10000):
            o.append(MTWidget())

class bench_widget_dispatch:
    '''Widget: event dispatch (1000 on_update in 10*1000 MTWidget)'''
    def __init__(self):
        root = MTWidget()
        for x in xrange(10):
            parent = MTWidget()
            for y in xrange(1000):
                parent.add_widget(MTWidget())
            root.add_widget(parent)
        self.root = root
    def run(self):
        root = self.root
        for x in xrange(1000):
            root.dispatch_event('on_update')

class bench_graphx_line:
    '''Graphx: draw lines (50000 x/y) 100 times'''
    def __init__(self):
        lines = []
        w, h = window_size
        for x in xrange(50000):
            lines.extend([random() * w, random() * h])
        self.lines = lines
    def run(self):
        lines = self.lines
        for x in xrange(100):
            drawLine(lines)

class bench_graphx_rectangle:
    '''Graphx: draw rectangle (50000 rect) 100 times'''
    def __init__(self):
        rects = []
        w, h = window_size
        for x in xrange(50000):
            rects.append(((random() * w, random() * h), (random() * w, random() * h)))
        self.rects = rects
    def run(self):
        rects = self.rects
        for x in xrange(100):
            for pos, size in rects:
                drawRectangle(pos=pos, size=size)

class bench_graphx_roundedrectangle:
    '''Graphx: draw rounded rectangle (5000 rect) 100 times'''
    def __init__(self):
        rects = []
        w, h = window_size
        for x in xrange(5000):
            rects.append(((random() * w, random() * h), (random() * w, random() * h)))
        self.rects = rects
    def run(self):
        rects = self.rects
        for x in xrange(100):
            for pos, size in rects:
                drawRoundedRectangle(pos=pos, size=size)


class bench_graphx_paintline:
    '''Graphx: paint line (500 x/y) 100 times'''
    def __init__(self):
        lines = []
        w, h = window_size
        for x in xrange(500):
            lines.extend([random() * w, random() * h])
        self.lines = lines
        set_brush(os.path.join(pymt_data_dir, 'particle.png'))
    def run(self):
        lines = self.lines
        for x in xrange(100):
            paintLine(lines)

if __name__ == '__main__':
    report = []
    report_newline = True
    def log(s, newline=True):
        global report_newline
        if not report_newline:
            report[-1] = '%s %s' % (report[-1], s)
        else:
            report.append(s)
        if newline:
            print s
            report_newline = True
        else:
            print s,
            report_newline = False
        sys.stdout.flush()

    clock_total = 0
    benchs = locals().keys()
    benchs.sort()
    benchs = [locals()[x] for x in benchs if x.startswith('bench_')]

    log('')
    log('=' * 70)
    log('PyMT Benchmark v%s' % benchmark_version)
    log('=' * 70)
    log('')
    log('System informations')
    log('-------------------')

    log('OS platform     : %s' % sys.platform)
    log('Python EXE      : %s' % sys.executable)
    log('Python Version  : %s' % sys.version)
    log('Python API      : %s' % sys.api_version)
    try:
        log('PyMT Version    : %s' % pymt.__version__)
    except:
        log('PyMT Version    : unknown (too old)')
    log('Install path    : %s' % os.path.dirname(pymt.__file__))
    log('Install date    : %s' % time.ctime(os.path.getctime(pymt.__file__)))

    log('')
    log('OpenGL informations')
    log('-------------------')

    log('PyOpenGL Version: %s' % OpenGL.__version__)
    log('GL Vendor: %s' % glGetString(GL_VENDOR))
    log('GL Renderer: %s' % glGetString(GL_RENDERER))
    log('GL Version: %s' % glGetString(GL_VERSION))
    log('')

    log('Benchmark')
    log('---------')
    for x in benchs:
        log('%2d/%-2d %-60s' % (benchs.index(x)+1, len(benchs), x.__doc__), False)
        try:
            test = x()
        except Exception, e:
            log('failed %s' % str(e))
            continue

        clock_start = clock()

        try:
            test.run()
            clock_end = clock() - clock_start
            log('%.6f' % clock_end)
        except Exception, e:
            log('failed %s' % str(e))
            continue

        clock_total += clock_end

    log('')
    log('Result: %.6f' % clock_total)
    log('')

try:
    getWindow().close()
except:
    pass

try:
    reply = raw_input('Do you want to send benchmark to paste.pocoo.org (Y/n) : ')
except EOFError:
    sys.exit(0)

if reply.lower().strip() in ('', 'y'):
    print 'Please wait while sending the benchmark...'

    from xmlrpclib import ServerProxy
    s = ServerProxy('http://paste.pocoo.org/xmlrpc/')
    r = s.pastes.newPaste('text', '\n'.join(report))

    print
    print
    print 'REPORT posted at http://paste.pocoo.org/show/%s/' % r
    print
    print
else:
    print 'No benchmark posted.'
