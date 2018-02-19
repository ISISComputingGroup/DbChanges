import os
import git
from multiprocessing import Process, cpu_count

from constants import EPICS_REPO_URL, LOG


def clone_epics_into_temp_dir(temp_dir, branchname):
    directory = os.path.join(temp_dir, branchname)
    gitcmd = git.Git(directory).execute

    if os.path.exists(directory):
        LOG.info("Directory {} already exists, skipping clone.".format(directory))
        return

    os.makedirs(directory)

    LOG.info("Cloning EPICS repo from {url} at branch {branch} into {directory}."
             .format(branch=branchname, url=EPICS_REPO_URL, directory=directory,))

    clone_options = [
        "--recurse-submodules",
        "--jobs {}".format(cpu_count()),
        "--single-branch",
        "--depth 1",
        "--branch {branch}".format(branch=branchname),
        EPICS_REPO_URL,
        ".",  # Clone into present directory
    ]

    gitcmd("git clone {options}".format(options=" ".join(clone_options), url=EPICS_REPO_URL))

    LOG.info("Finished cloning into {}.".format(directory))


def clone_repos(temp_dir, repos):
    threads = [Process(target=clone_epics_into_temp_dir, args=(temp_dir, repo)) for repo in repos]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
