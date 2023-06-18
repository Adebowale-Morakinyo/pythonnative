import argparse
import os
import shutil
import subprocess


def init_project(args: argparse.Namespace) -> None:
    """
    Initialize a new PythonNative project.
    """
    # TODO: Implementation


def create_android_project(project_name: str, destination: str) -> bool:
    """
    Create a new Android project using android command.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    :return: True if the project was created successfully, False otherwise.
    """
    # The command to create a new Android project
    command = f"cd {destination} && android create project --name {project_name} --path . --target android-30 --package com.example.{project_name} --activity MainActivity"

    # Run the command
    process = subprocess.run(command, shell=True, check=True, text=True)

    return process.returncode == 0


def create_ios_project(project_name: str, destination: str) -> bool:
    """
    Create a new Xcode project using xcodeproj gem.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    :return: True if the project was created successfully, False otherwise.
    """
    # The command to create a new Xcode project
    command = f"cd {destination} && xcodeproj new {project_name}.xcodeproj"

    # Run the command
    process = subprocess.run(command, shell=True, check=True, text=True)

    return process.returncode == 0


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
