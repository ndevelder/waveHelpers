import glob
import os
import re

import llnl.util.tty as tty

from spack.package import *
from spack.pkg.builtin.boost import Boost
from spack.util.environment import EnvironmentModifications


class Oceanwave3d(Package):
    """waves2Foam is a third party add-on to OpenFOAM
    """

    maintainers = ["ndevelder"]
    homepage = "https://github.com/ndevelder/waveSolvers"

    version("main", git="https://github.com/ndevelder/waveSolvers.git", preferred=True)

    depends_on("openfoam@2106_220610")
    depends_on("gsl")
    depends_on("waves2foam")

    phases = ["configure", "build"]
    build_script = "./Allwmake"

    def setup_minimal_environment(self, env):
        """Sets a minimal openfoam environment."""
        pass

    def setup_build_environment(self, env):
        """Sets the build environment (prior to unpacking the sources)."""
        env.set("WAVES_GSL_INCLUDE", self.spec["gsl"].prefix.include)
        env.set("WAVES_GSL_LIB", self.spec["gsl"].prefix.lib)
        env.set("FFLAGS","-fallow-argument-mismatch")
        pass

    def setup_run_environment(self, env):
        """Sets the build environment (prior to unpacking the sources)."""
        env.prepend_path("LD_LIBRARY_PATH", self.spec["gsl"].prefix.lib)
        pass

    def configure(self, spec, prefix):
        pass

    def build(self, spec, prefix):
        #self.foam_arch.has_rule(self.stage.source_path)
        #self.foam_arch.create_rules(self.stage.source_path, self)


        args = [""]
        if self.parallel:  # Build in parallel? - pass as an argument
            args.append("-j{0}".format(make_jobs))
        builder = Executable(self.build_script)
        builder(*args)

    #def install(self, spec, prefix):
    #    return True