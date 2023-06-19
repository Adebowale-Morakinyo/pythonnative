import argparse
import os
import shutil
import subprocess
import requests
import zipfile
import io


def init_project(args: argparse.Namespace) -> None:
    """
    Initialize a new PythonNative project.
    """
    # TODO: Implementation


def download_template_project(template_url: str, destination: str) -> None:
    """
    Download and extract a template project from a URL.

    :param template_url: The URL of the template project.
    :param destination: The directory where the project will be created.
    """
    response = requests.get(template_url, stream=True)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(destination)


def create_android_project(project_name: str, destination: str) -> bool:
    """
    Create a new Android project using a template.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    :return: True if the project was created successfully, False otherwise.
    """
    android_template_url = "https://github.com/owenthcarey/pythonnative-workspace/blob/main/apps/templates/android_template.zip?raw=true"

    # Download and extract the Android template project
    download_template_project(android_template_url, destination)

    return True


def create_ios_project(project_name: str, destination: str) -> bool:
    """
    Create a new iOS project using a template.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    :return: True if the project was created successfully, False otherwise.
    """
    ios_template_url = "https://github.com/owenthcarey/pythonnative-workspace/blob/main/apps/templates/ios_template.zip?raw=true"

    # Download and extract the iOS template project
    download_template_project(ios_template_url, destination)

    return True


def run_project(args: argparse.Namespace) -> None:
    """
    Run the specified project.
    """
    # Determine the platform
    platform = args.platform

    # Define the build directory
    build_dir = os.path.join(os.getcwd(), "build", platform)

    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)

    # Generate the required project files
    if platform == "android":
        create_android_project("MyApp", build_dir)
    elif platform == "ios":
        create_ios_project("MyApp", build_dir)

    # Copy the user's Python code into the project
    src_dir = os.path.join(os.getcwd(), "app")
    dest_dir = os.path.join(
        build_dir, "app"
    )  # You might need to adjust this depending on the project structure
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)

    # Install any necessary Python packages into the project environment
    requirements_file = os.path.join(os.getcwd(), "requirements.txt")
    # TODO: Fill in with actual commands for installing Python packages

    # Run the project
    # TODO: Fill in with actual commands for running the project


def clean_project(args: argparse.Namespace) -> None:
    """
    Clean the specified project.
    """
    # Define the build directory
    build_dir = os.path.join(os.getcwd(), "build")

    # Check if the build directory exists
    if os.path.exists(build_dir):
        # Delete the build directory
        shutil.rmtree(build_dir)


def main() -> None:
    parser = argparse.ArgumentParser(prog="pn", description="PythonNative CLI")
    subparsers = parser.add_subparsers()

    # Create a new command 'init' that calls init_project
    parser_init = subparsers.add_parser("init")
    parser_init.set_defaults(func=init_project)

    # Create a new command 'run' that calls run_project
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("platform", choices=["android", "ios"])
    parser_run.set_defaults(func=run_project)

    # Create a new command 'clean' that calls clean_project
    parser_clean = subparsers.add_parser("clean")
    parser_clean.set_defaults(func=clean_project)

    args = parser.parse_args()
    args.func(args)
