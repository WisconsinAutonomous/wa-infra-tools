from wa_infra_tools.mars_utils import clone_mars, download, upload, remove

def upload_model(model_name, category, model_dir, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    upload_path = "models/" + category + "/" + model_name
    if commit_message is None:
        commit_message = f"Uploaded model {model_name} in category {category}"
    upload(model_dir, upload_path, mars_dir, branch, commit_message, commit_changes, push_changes)

def download_model(model_name, category, output_dir, mars_dir=None, branch=None):
    download("models/" + category + "/" + model_name, output_dir, mars_dir, branch)

def remove_model(model_name, category, mars_dir=None, branch=None, commit_message=None, commit_changes=True, push_changes=True):
    del_path = "models/" + category + "/" + model_name
    if commit_message is None:
        commit_message = f"Removed model {model_name} in category {category}"
    remove(del_path, mars_dir, branch, commit_message, commit_changes, push_changes)
