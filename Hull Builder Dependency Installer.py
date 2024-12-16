#Author - Bennett Steers
#Description - Installs required dependencies for the hull builder script. 
#Run this before you run the hull builder for the first time or you will get errors

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys, subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "numpy"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "scipy"]) 