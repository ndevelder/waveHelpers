import glob
import os
import re

import llnl.util.tty as tty

from spack.package import *
from spack.pkg.builtin.boost import Boost
from spack.util.environment import EnvironmentModifications

__all__ = [
    "rewrite_environ_files",
]

def rewrite_environ_files(environ, **kwargs):
    """Use filter_file to rewrite (existing) POSIX shell or C-shell files.
    Keyword Options:
    posix[=None]    If set, the name of the POSIX file to rewrite.
    cshell[=None]   If set, the name of the C-shell file to rewrite.
    """
    print("Rewriting bashrc.org")
    rcfile = kwargs.get("posix", None)
    if rcfile and os.path.isfile(rcfile):
        for k, v in environ.items():
            regex = r"^(\s*export\s+{0})=.*$".format(k)
            print("Regex:", regex)
            if not v:
                replace = r"unset {0}  #SPACK: unset".format(k)
            elif v.startswith("#"):
                replace = r"unset {0}  {1}".format(k, v)
            else:
                replace = r"\1={0}".format(v)
            print("Replace: ",replace)
            filter_file(regex, replace, rcfile, backup=False)

    rcfile = kwargs.get("cshell", None)
    if rcfile and os.path.isfile(rcfile):
        for k, v in environ.items():
            regex = r"^(\s*setenv\s+{0})\s+.*$".format(k)
            if not v:
                replace = r"unsetenv {0}  #SPACK: unset".format(k)
            elif v.startswith("#"):
                replace = r"unsetenv {0}  {1}".format(k, v)
            else:
                replace = r"\1 {0}".format(v)
            filter_file(regex, replace, rcfile, backup=False)

class Waves2foam(Package):
    """waves2Foam is a third party add-on to OpenFOAM
    """

    maintainers = ["ndevelder"]
    homepage = "https://openfoamwiki.net/index.php/Contrib/waves2Foam"

    version("svnlatest", svn="http://svn.code.sf.net/p/openfoam-extend/svn/trunk/Breeder_1.6/other/waves2Foam")
    version("gitlatest", git="https://github.com/ogoe/waves2Foam.git", preferred=True)

    depends_on("openfoam@2106_220610")
    depends_on("gsl")
    #depends_on("netlib-lapack@3.3.1")
    #depends_on("sparskit")
    #depends_on("oceanwave3d")
    #depends_on("fenton4foam")

    phases = ["configure", "build", "install"]
    build_script = "./Allwmake"

    def patch(self):
        """Adjust OpenFOAM build for spack.
        Where needed, apply filter as an alternative to normal patching."""
        #add_extra_files(self, self.common, self.assets)

    def setup_minimal_environment(self, env):
        """Sets a minimal openfoam environment."""
        pass

    def setup_build_environment(self, env):
        """Sets the build environment (prior to unpacking the sources)."""
        env.set("WAVES_GSL_INCLUDE", self.spec["gsl"].prefix.include)
        env.set("WAVES_GSL_LIB", self.spec["gsl"].prefix.lib)
        env.set("FFLAGS","-fallow-argument-mismatch")

    def setup_run_environment(self, env):
        """Sets the build environment (prior to unpacking the sources)."""
        pass

    def setup_dependent_build_environment(self, env, dependent_spec):
        self.setup_run_environment(env)
        env.set("WAVES_SRC", join_path(self.prefix, "src"))
        env.set("WAVES_LIBBIN", self.spec["openfoam"].prefix.lib)
        env.set("WAVES_GSL_INCLUDE", self.spec["gsl"].prefix.include)
        env.set("WAVES_GSL_LIB", self.spec["gsl"].prefix.lib)

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.setup_run_environment(env)
        env.set("WAVES_SRC", join_path(self.prefix, "src")) 
        env.set("WAVES_GSL_INCLUDE", self.spec["gsl"].prefix.include)
        env.set("WAVES_GSL_LIB", self.spec["gsl"].prefix.lib)

    def configure(self, spec, prefix):
        print('self.prefix: ',self.prefix)
        print('self.stage.source_path',self.stage.source_path)

        # Filtering: bashrc, cshrc
        edits = {
            "WAVES_DIR": self.stage.source_path,
            "WAVES_APPBIN": '$FOAM_APPBIN',
            "WAVES_LIBBIN": '$FOAM_LIBBIN',
            "WAVES_GSL_INCLUDE": self.spec["gsl"].prefix.include,
            "WAVES_GSL_LIB": self.spec["gsl"].prefix.lib,
        }

        bin_dir = join_path(self.stage.source_path, "bin")
        rewrite_environ_files(  # Adjust etc/bashrc and etc/cshrc
            edits, posix=join_path(bin_dir, "bashrc.org")
        )

    def build(self, spec, prefix):
        #self.foam_arch.has_rule(self.stage.source_path)
        #self.foam_arch.create_rules(self.stage.source_path, self)


        args = [""]
        if self.parallel:  # Build in parallel? - pass as an argument
            args.append("-j{0}".format(make_jobs))
        builder = Executable(self.build_script)
        builder(*args)

    def install(self, spec, prefix):
        mkdirp(self.prefix)

        # All top-level files, except spack build info
        ignored = re.compile(r"^spack-.*")

        files = [f for f in glob.glob("*") if os.path.isfile(f)]
        for f in files:
            install(f, self.prefix)

        # Having wmake and ~source is actually somewhat pointless...
        # Install 'etc' before 'bin' (for symlinks)
        # META-INFO for 1812 and later (or backported)
        dirs = ["applications", "bin", "doc", "lib", "src", "ThirdParty"]

        for d in dirs:
            if os.path.isdir(d):
                install_tree(d, join_path(self.prefix, d), symlinks=True)

        #self.install_write_location()
        #self.install_links()
