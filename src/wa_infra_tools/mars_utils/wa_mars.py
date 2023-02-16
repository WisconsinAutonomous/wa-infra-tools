from wa_infra_tools import mars_utils
import argparse
import os

def parse_args():
    parent_parser = argparse.ArgumentParser(description="wa_mars entry point")
    subparsers = parent_parser.add_subparsers(title="storage types")
    
    # models
    model_parser = subparsers.add_parser(
            "model",
            description="wa_mars model entrypoint",
            help="entrypoint to model commands")
    model_subparsers = model_parser.add_subparsers(title="commands")

    upload_model_parser = model_subparsers.add_parser(
            "upload",
            description="wa_mars model upload parser",
            help="upload a model to MARS")
    upload_model_parser.add_argument("model_name", type=str, help="name of the model to upload")
    upload_model_parser.add_argument("category", type=str, help="category of model")
    upload_model_parser.add_argument("model_dir", type=str, help="where the model is currently stored")
    upload_model_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    upload_model_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    upload_model_parser.add_argument("-m", "--message", type=str, help="commit message")
    upload_model_parser.add_argument("--no-commit", action="store_false", help="do not commit changes")
    upload_model_parser.add_argument("--no-push", action="store_false", help="do not push changes")
    upload_model_parser.set_defaults(func=lambda args: mars_utils.models.upload_model(args.model_name, args.category, args.model_dir, args.mars_dir, args.branch, args.message, args.no_commit, args.no_push))
    
    download_model_parser = model_subparsers.add_parser(
            "download",
            description="wa_mars model download parser",
            help="download a model from MARS")
    download_model_parser.add_argument("model_name", type=str, help="name of the model to download")
    download_model_parser.add_argument("category", type=str, help="category of model")
    download_model_parser.add_argument("output_dir", type=str, help="where to save the model")
    download_model_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    download_model_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    download_model_parser.set_defaults(func=lambda args: mars_utils.models.download_model(args.model_name, args.category, args.output_dir, args.mars_dir, args.branch))

    remove_model_parser = model_subparsers.add_parser(
            "remove",
            description="wa_mars model remove parser",
            help="remove models in MARS")
    remove_model_parser.add_argument("model_name", type=str, help="name of the model to remove")
    remove_model_parser.add_argument("category", type=str, help="category of model")
    remove_model_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    remove_model_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    remove_model_parser.add_argument("-m", "--message", type=str, help="commit message")
    remove_model_parser.add_argument("--no-commit", action="store_false", help="do not commit changes")
    remove_model_parser.add_argument("--no-push", action="store_false", help="do not push changes")
    remove_model_parser.set_defaults(func=lambda args: mars_utils.models.remove_model(args.model_name, args.category, args.mars_dir, args.branch, args.message, args.no_commit, args.no_push))


    # rosbags
    rosbag_parser = subparsers.add_parser(
            "rosbag",
            description="wa_mars rosbag entrypoint",
            help="entrypoint to rosbag commands")
    rosbag_subparsers = rosbag_parser.add_subparsers(title="commands")

    record_rosbag_parser = rosbag_subparsers.add_parser(
            "record",
            description="wa_mars rosbag record",
            help="record a rosbag")
    record_rosbag_parser.add_argument("topics", nargs="*", help="list of topics to record")
    record_rosbag_parser.add_argument("-u", "--upload", action="store_true", help="upload rosbag to MARS (only done if output dir (rosbag name) is specified)")
    record_rosbag_parser.add_argument("-o", "--output", type=str, help="name of the directory to save the rosbag into")
    record_rosbag_parser.set_defaults(func=lambda args:mars_utils.rosbags.record_rosbag(args.topics, args.upload, args.output))

    upload_rosbag_parser = rosbag_subparsers.add_parser(
            "upload",
            description="wa_mars rosbag upload parser",
            help="upload a rosbag to MARS")
    upload_rosbag_parser.add_argument("rosbag_name", type=str, help="name of the rosbag to upload")
    upload_rosbag_parser.add_argument("rosbag_dir", type=str, help="where the rosbag is currently stored")
    upload_rosbag_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    upload_rosbag_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    upload_rosbag_parser.add_argument("-m", "--message", type=str, help="commit message")
    upload_rosbag_parser.add_argument("--no-commit", action="store_false", help="do not commit changes")
    upload_rosbag_parser.add_argument("--no-push", action="store_false", help="do not push changes")
    upload_rosbag_parser.set_defaults(func=lambda args: mars_utils.rosbags.upload_rosbag(args.rosbag_name, args.category, args.rosbag_dir, args.mars_dir, args.branch, args.message, args.no_commit, args.no_push))
    
    download_rosbag_parser = rosbag_subparsers.add_parser(
            "download",
            description="wa_mars rosbag download parser",
            help="download a rosbag from MARS")

    download_rosbag_parser.add_argument("rosbag_name", type=str, help="name of the rosbag to download")
    download_rosbag_parser.add_argument("output_dir", type=str, help="where to save the rosbag")
    download_rosbag_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    download_rosbag_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    download_rosbag_parser.set_defaults(func=lambda args: mars_utils.rosbags.download_rosbag(args.rosbag_name, args.category, args.output_dir, args.mars_dir, args.branch))

    remove_rosbag_parser = rosbag_subparsers.add_parser(
            "remove",
            description="wa_mars rosbag remove parser",
            help="remove rosbags in MARS")
    remove_rosbag_parser.add_argument("rosbag_name", type=str, help="name of the rosbag to remove")
    remove_rosbag_parser.add_argument("--mars-dir", type=str, help="where the MARS repo is (default: crate a temporary MARS repo)")
    remove_rosbag_parser.add_argument("-b", "--branch", type=str, help="which branch of MARS to check out")
    remove_rosbag_parser.add_argument("-m", "--message", type=str, help="commit message")
    remove_rosbag_parser.add_argument("--no-commit", action="store_false", help="do not commit changes")
    remove_rosbag_parser.add_argument("--no-push", action="store_false", help="do not push changes")
    remove_rosbag_parser.set_defaults(func=lambda args: mars_utils.rosbags.remove_rosbag(args.rosbag_name, args.category, args.mars_dir, args.branch, args.message, args.no_commit, args.no_push))

    args = parent_parser.parse_args()
    return args

def main():
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
