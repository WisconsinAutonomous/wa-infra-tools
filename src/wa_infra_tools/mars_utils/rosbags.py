from wa_infra_tools.mars_utils import clone_mars, download, upload, remove
import subprocess

def record_rosbag(topics=None, upload=False, output_dir=None):
    command = ["ros2", "bag", "record"]
    if output_dir:
        command.append(f"-o {output_dir}")

    if topics:
        command += topics
    else:
        command.append("-a")
    subprocess.run(command)
    if upload and output_dir is not None:
        upload_rosbag(output_dir, output_dir)

def upload_rosbag(rosbag_name, rosbag_dir, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    upload_path = "rosbags/" + rosbag_name
    if commit_message is None:
        commit_message = "Uploaded rosbag {rosbag_name}"
    upload(rosbag_dir, upload_path, mars_dir, commit_message, commit_changes, push_changes)

def download_rosbag(rosbag_name, output_dir, mars_dir=None, branch=None):
    download("rosbags/" + rosbag_name, output_dir, mars_dir)

def remove_rosbag(rosbag_name, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    del_path = "rosbags/" + rosbag_name
    if commit_message is None:
        commit_message = "Removed rosbag {rosbag_name}"
    remove(del_path, mars_dir, branch, commit_message, commit_changes, push_changes)
