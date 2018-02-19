import logging
import os
import sys


LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.setLevel(logging.INFO)

TEMP_DIR = os.path.abspath(os.path.join("C:\\", "Instrument", "Var", "tmp", "DbChanges"))
EPICS_REPO_URL = "https://github.com/ISISComputingGroup/EPICS.git"
