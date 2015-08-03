import sys, os
from cx_Freeze import setup, Executable
  
#############################################################################
# Options setup 
  
# Modules path
path = sys.path

# Includes/excludes options
includes = ["gi"]
excludes = []
packages = ["gi"]
  
# Copy files/folder
includefiles = [("config","config"), ("remote.sh","remote.sh")]

# Additional libs
binpathincludes = []

  
# Option dict
options = {"path": path,
	"includes": includes,
	"excludes": excludes,
	"packages": packages,
	"include_files": includefiles,
	"bin_path_includes": binpathincludes,
	"build_exe":"Foo.cd",
	"optimize": 2
	}
  
#############################################################################
# Target preparation
base = None
if sys.platform == "win32":
	base = "Win32GUI"
  
target = Executable(
	script = "main.py",
	base = base,
	targetName = "Foo.cd",
	compress = True,
	icon = None
	)
  
#############################################################################
# Setup creation
setup(
    name = "Foo.CD",
    version = "0.1",
    description = "Music player",
    author = "Wootwoot",
    options = {"build_exe": options},
    executables = [target]
    )