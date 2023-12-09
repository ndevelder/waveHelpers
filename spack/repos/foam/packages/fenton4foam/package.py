import glob
import os
import re

import llnl.util.tty as tty

from spack.package import *
from spack.pkg.builtin.boost import Boost
from spack.util.environment import EnvironmentModifications


class Fenton4foam(MakefilePackage):
    """Fenton4Foam is a third party add-on to waves2foam
    """

    maintainers = ["ndevelder"]
    homepage = "https://github.com/ndevelder/fenton4Foam"

    version("main", git="https://github.com/ndevelder/fenton4Foam.git", preferred=True)

    # We provide the standard Make flags here:
    # https://spack.readthedocs.io/en/latest/packaging_guide.html?highlight=flag_handler#compiler-flags
    def flag_handler(self, name, flags):
        spec = self.spec
        if "+pic" in spec:
            if name == "fflags":
                flags.append(self.compiler.fc_pic_flag)
        if name == "fflags":
            if "gfortran" in self.compiler.fc:
                flags.append("-std=legacy")
                flags.append("-Wall")
        if "+debug" in spec:
            if "-g" in self.compiler.debug_flags:
                flags.append("-g")
            if "-O0" in self.compiler.opt_flags:
                flags.append("-O0")
            elif "-O" in self.compiler.opt_flags:
                flags.append("-O")
        else:
            if "-O3" in self.compiler.opt_flags:
                flags.append("-O3")
            elif "-O2" in self.compiler.opt_flags:
                flags.append("-O2")

        return (None, flags, None)

    def edit(self, spec, prefix):
        mkfile = FileFilter("makefile")
        mkfile.filter(r"^(OPT).*=.+", r"\1= -c $(FFLAGS)")

    def build(self, spec, prefix):
        make("clean")
        make("F77={0}".format(spack_fc))

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install("fenton4Foam", prefix.bin)
