from wa_infra_tools import git_utils
from distutils.dir_util import copy_tree, remove_tree
import os

def clone_mars(branch=None, mars_dir=None):
    try:
        git_utils.clone("git@github.com:WisconsinAutonomous/MARS.git", branch, mars_dir)
        return
    except:
        print("ssh clone of MARS failed")

    try:
        git_utils.clone("https://github.com/WisconsinAutonomous/MARS.git", branch, mars_dir)
        return
    except:
        print("https clone of MARS failed")

def upload(source_path, upload_path, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    del_mars = False # delete mars repo after operation
    if mars_dir is None: # create temporary repo
        clone_mars(branch=branch)
        mars_dir = "MARS"
        del_mars = True

    # upload files
    dest_path = mars_dir + "/" + upload_path
    os.makedirs(dest_path, exist_ok=True)
    copy_tree(source_path, dest_path)
    git_utils.add(mars_dir, [upload_path], capture_output=False)
    if commit_changes:
        git_utils.commit(mars_dir, commit_message, capture_output=False)
        if push_changes:
            git_utils.push(mars_dir, capture_output=False)

    # delete temp repo
    if del_mars:
        remove_tree(mars_dir)


def download(local_path, output_dir, mars_dir=None, branch=None):
    del_mars = False # delete mars repo after operation
    if mars_dir is None: # create temporary repo
        clone_mars(branch=branch)
        mars_dir = "MARS"
        del_mars = True

    # pull files
    git_utils.pull(mars_dir, capture_output=False)
    git_utils.lfs_pull(mars_dir, includes=local_path, capture_output=False)
    src_path = mars_dir + "/"  + local_path
    copy_tree(src_path, output_dir)

    # delete temp repo
    if del_mars:
        remove_tree(mars_dir)

def remove(local_path, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    del_mars = False # delete mars repo after operation
    if mars_dir is None: # create temporary repo
        clone_mars(branch=branch)
        mars_dir = "MARS"
        del_mars = True

    # remove files
    remove_tree(mars_dir + "/" + local_path)
    git_utils.add(mars_dir, [local_path], capture_output=False)
    if commit_changes:
        git_utils.commit(mars_dir, commit_message, capture_output=False)
        if push_changes:
            git_utils.push(mars_dir, capture_output=False)

    # delete temp repo
    if del_mars:
        remove_tree(mars_dir)

