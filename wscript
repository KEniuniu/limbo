#!/usr/bin/env python
# encoding: utf-8
#| Copyright Inria May 2015
#| This project has received funding from the European Research Council (ERC) under
#| the European Union's Horizon 2020 research and innovation programme (grant
#| agreement No 637972) - see http://www.resibots.eu
#|
#| Contributor(s):
#|   - Jean-Baptiste Mouret (jean-baptiste.mouret@inria.fr)
#|   - Antoine Cully (antoinecully@gmail.com)
#|   - Kontantinos Chatzilygeroudis (konstantinos.chatzilygeroudis@inria.fr)
#|   - Federico Allocati (fede.allocati@gmail.com)
#|   - Vaios Papaspyros (b.papaspyros@gmail.com)
#|   - Roberto Rama (bertoski@gmail.com)
#|
#| This software is a computer library whose purpose is to optimize continuous,
#| black-box functions. It mainly implements Gaussian processes and Bayesian
#| optimization.
#| Main repository: http://github.com/resibots/limbo
#| Documentation: http://www.resibots.eu/limbo
#|
#| This software is governed by the CeCILL-C license under French law and
#| abiding by the rules of distribution of free software.  You can  use,
#| modify and/ or redistribute the software under the terms of the CeCILL-C
#| license as circulated by CEA, CNRS and INRIA at the following URL
#| "http://www.cecill.info".
#|
#| As a counterpart to the access to the source code and  rights to copy,
#| modify and redistribute granted by the license, users are provided only
#| with a limited warranty  and the software's author,  the holder of the
#| economic rights,  and the successive licensors  have only  limited
#| liability.
#|
#| In this respect, the user's attention is drawn to the risks associated
#| with loading,  using,  modifying and/or developing or reproducing the
#| software by the user in light of its specific status of free software,
#| that may mean  that it is complicated to manipulate,  and  that  also
#| therefore means  that it is reserved for developers  and  experienced
#| professionals having in-depth computer knowledge. Users are therefore
#| encouraged to load and test the software's suitability as regards their
#| requirements in conditions enabling the security of their systems and/or
#| data to be ensured and,  more generally, to use and operate it in the
#| same conditions as regards security.
#|
#| The fact that you are presently reading this means that you have had
#| knowledge of the CeCILL-C license and that you accept its terms.
#|
import sys
sys.path.insert(0, './waf_tools')

VERSION = '0.0.1'
APPNAME = 'limbo'

srcdir = '.'
blddir = 'build'

import glob
import os
import subprocess
import limbo
import inspect
from waflib import Logs
from waflib.Build import BuildContext

def options(opt):
        opt.load('compiler_cxx boost waf_unit_test')
        opt.load('compiler_c')
        opt.load('eigen')
        opt.load('tbb')
        opt.load('mkl')
        opt.load('sferes')
        opt.load('limbo')
        opt.load('openmp')
        opt.load('nlopt')
        opt.load('libcmaes')
        opt.load('xcode')

        opt.add_option('--create', type='string', help='create a new exp', dest='create_exp')
        limbo.add_create_options(opt)
        opt.add_option('--exp', type='string', help='exp(s) to build, separate by comma', dest='exp')
        opt.add_option('--qsub', type='string', help='config file (json) to submit to torque', dest='qsub')
        opt.add_option('--oar', type='string', help='config file (json) to submit to oar', dest='oar')
        opt.add_option('--local', type='string', help='config file (json) to run local', dest='local')
        opt.add_option('--local_serial', type='string', help='config file (json) to run local', dest='local_serial')
        opt.add_option('--experimental', action='store_true', help='specify to compile the experimental examples', dest='experimental')
        opt.add_option('--nb_replicates', type='int', help='number of replicates performed during the benchmark', dest='nb_rep')
        opt.add_option('--tests', action='store_true', help='compile tests or not', dest='tests')
        opt.add_option('--write_params', type='string', help='write all the default values of parameters in a file (used by the documentation system)', dest='write_params')

        for i in glob.glob('exp/*'):
                if os.path.isdir(i):
                    opt.recurse(i)

        opt.recurse('src/benchmarks')

def configure(conf):
        conf.load('compiler_cxx boost waf_unit_test')
        conf.load('compiler_c')
        conf.load('eigen')
        conf.load('tbb')
        conf.load('sferes')
        conf.load('openmp')
        conf.load('mkl')
        conf.load('xcode')
        conf.load('nlopt')
        conf.load('libcmaes')

        native_flags = "-march=native"
        if conf.env.CXX_NAME in ["icc", "icpc"]:
            common_flags = "-Wall -std=c++11"
            opt_flags = " -O3 -xHost -g"
            native_flags = "-mtune=native -unroll -fma"
        else:
            if conf.env.CXX_NAME in ["gcc", "g++"] and int(conf.env['CC_VERSION'][0]+conf.env['CC_VERSION'][1]) < 47:
                common_flags = "-Wall -std=c++0x"
            else:
                common_flags = "-Wall -std=c++11"
            if conf.env.CXX_NAME in ["clang", "llvm"]:
                common_flags += " -fdiagnostics-color"
            opt_flags = " -O3 -g"

        native = conf.check_cxx(cxxflags=native_flags, mandatory=False, msg='Checking for compiler flags \"'+native_flags+'\"')
        if native:
            opt_flags = opt_flags + ' ' + native_flags
        else:
            Logs.pprint('YELLOW', 'WARNING: Native flags not supported. The performance might be a bit deteriorated.')

        conf.check_boost(lib='serialization filesystem \
            system unit_test_framework program_options \
            thread', min_version='1.39')
        conf.check_eigen()
        conf.check_tbb()
        conf.check_sferes()
        conf.check_openmp()
        conf.check_mkl()
        conf.check_nlopt()
        conf.check_libcmaes()

        conf.env.INCLUDES_LIMBO = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/src"

        all_flags = common_flags + opt_flags
        conf.env['CXXFLAGS'] = conf.env['CXXFLAGS'] + all_flags.split(' ')
        Logs.pprint('NORMAL', 'CXXFLAGS: %s' % conf.env['CXXFLAGS'])

        if conf.options.exp:
                for i in conf.options.exp.split(','):
                        Logs.pprint('NORMAL', 'configuring for exp: %s' % i)
                        conf.recurse('exp/' + i)
        conf.recurse('src/benchmarks')
        Logs.pprint('NORMAL', '')
        Logs.pprint('NORMAL', 'WHAT TO DO NOW?')
        Logs.pprint('NORMAL', '---------------')
        Logs.pprint('NORMAL', '[users] To compile Limbo: ./waf build')
        Logs.pprint('NORMAL', '[users] To compile and run unit tests: ./waf --tests')
        Logs.pprint('NORMAL', '[users] Read the documentation (inc. tutorials) on http://www.resibots.eu/limbo')
        Logs.pprint('NORMAL', '[developers] To compile the HTML documentation (this requires sphinx and the resibots theme): ./waf docs')
        Logs.pprint('NORMAL', '[developers] To compile the benchmarks: ./waf build_benchmark')
        Logs.pprint('NORMAL', '[developers] To compile the extensive tests: ./waf build_extensive_tests')


def build(bld):
    if bld.options.write_params:
        limbo.write_default_params(bld.options.write_params)
        Logs.pprint('NORMAL', 'default parameters written in %s' % bld.options.write_params)
    bld.recurse('src/')
    if bld.options.exp:
        for i in bld.options.exp.split(','):
            Logs.pprint('NORMAL', 'Building exp: %s' % i)
            bld.recurse('exp/' + i)
            limbo.output_params('exp/'+i)
    bld.add_post_fun(limbo.summary)

def build_extensive_tests(ctx):
    ctx.recurse('src/')
    ctx.recurse('src/tests')

def build_benchmark(ctx):
    ctx.recurse('src/benchmarks')

def run_extensive_tests(ctx):
    for fullname in glob.glob('build/src/tests/combinations/*'):
        if os.path.isfile(fullname) and os.access(fullname, os.X_OK):
            fpath, fname = os.path.split(fullname)
            Logs.pprint('NORMAL', 'Running: %s' % fname)
            s = "cd " + fpath + "; ./" + fname
            retcode = subprocess.call(s, shell=True, env=None)

def submit_extensive_tests(ctx):
    for fullname in glob.glob('build/src/tests/combinations/*'):
        if os.path.isfile(fullname) and os.access(fullname, os.X_OK):
            fpath, fname = os.path.split(fullname)
            s = "cd " + fpath + ";oarsub -l /nodes=1/core=2,walltime=00:15:00 -n " + fname + " -O " + fname + ".stdout.%jobid%.log -E " + fname + ".stderr.%jobid%.log ./" + fname
            retcode = subprocess.call(s, shell=True, env=None)
            Logs.pprint('NORMAL', 'oarsub returned: %s' % str(retcode))

def run_benchmark(ctx):
    HEADER='\033[95m'
    NC='\033[0m'
    res_dir=os.getcwd()+"/benchmark_results/"
    try:
        os.makedirs(res_dir)
    except:
        Logs.pprint('YELLOW', 'WARNING: directory \'%s\' could not be created!' % res_dir)
    for fullname in glob.glob('build/src/benchmarks/*'):
        if os.path.isfile(fullname) and os.access(fullname, os.X_OK):
            fpath, fname = os.path.split(fullname)
            directory = res_dir + "/" + fname
            try:
                os.makedirs(directory)
            except:
                Logs.pprint('YELLOW', 'WARNING: directory \'%s\' could not be created, the new results will be concatenated to the old ones' % directory)
            s = "cp " + fullname + " " + directory
            retcode = subprocess.call(s, shell=True, env=None)
            if ctx.options.nb_rep:
                nb_rep = ctx.options.nb_rep
            else:
                nb_rep = 10
            for i in range(0,nb_rep):
                Logs.pprint('NORMAL', '%s Running: %s for the %s th time %s' % (HEADER, fname, str(i), NC))
                s="cd " + directory +";./" + fname
                retcode = subprocess.call(s, shell=True, env=None)

def shutdown(ctx):
    if ctx.options.create_exp:
        limbo.create_exp(ctx.options.create_exp, ctx.options)
    if ctx.options.qsub:
        limbo.qsub(ctx.options.qsub)
    if ctx.options.oar:
        limbo.oar(ctx.options.oar)
    if ctx.options.local:
        limbo.run_local(ctx.options.local, False)
    if ctx.options.local_serial:
        limbo.run_local(ctx.options.local_serial)

def insert_license(ctx):
    limbo.insert_license()

def write_default_params(ctx):
    Logs.pprint('NORMAL', 'extracting default params to docs/defaults.rst')
    limbo.write_default_params('docs/defaults.rst')

def build_docs(ctx):
    Logs.pprint('NORMAL', "generating HTML doc with versioning...")
    s = 'sphinx-versioning -v build -f docs/pre_script.sh --whitelist-branches "(new_benchmarks|master|release-*)" docs docs/_build/html'
    retcode = subprocess.call(s, shell=True, env=None)

class BuildExtensiveTestsContext(BuildContext):
    cmd = 'build_extensive_tests'
    fun = 'build_extensive_tests'

class BuildBenchmark(BuildContext):
    cmd = 'build_benchmark'
    fun = 'build_benchmark'

class InsertLicense(BuildContext):
    cmd = 'insert_license'
    fun = 'insert_license'

class BuildDoc(BuildContext):
    cmd = 'docs'
    fun = 'build_docs'

class BuildDoc(BuildContext):
    cmd = 'default_params'
    fun = 'write_default_params'
