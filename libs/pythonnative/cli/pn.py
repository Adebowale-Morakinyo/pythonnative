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

    # Adjust the destination directory for Android project
    if platform == "android":
        dest_dir = os.path.join(build_dir, "android_template", "app", "src", "main", "python", "app")
    elif platform == "ios":
        dest_dir = os.path.join(build_dir, "app")  # Adjust this based on your iOS project structure

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)

    # Install any necessary Python packages into the project environment
    requirements_file = os.path.join(os.getcwd(), "requirements.txt")
    # TODO: Fill in with actual commands for installing Python packages

    # Run the project
    if platform == "android":
        # Change to the Android project directory
        android_project_dir = os.path.join(build_dir, "android_template")
        os.chdir(android_project_dir)

        # Add executable permissions to the gradlew script
        gradlew_path = os.path.join(android_project_dir, "gradlew")
        os.chmod(gradlew_path,
                 0o755)  # this makes the file executable for the user

        # Build the Android project and install it on the device
        jdk_path = subprocess.check_output(
            ["brew", "--prefix", "openjdk@17"]).decode().strip()
        env = os.environ.copy()
        env["JAVA_HOME"] = jdk_path
        subprocess.run(["./gradlew", "installDebug"], check=True, env=env)

        # Run the Android app
        # Assumes that the package name of your app is "com.example.myapp" and the main activity is "MainActivity"
        # Replace "com.example.myapp" and ".MainActivity" with your actual package name and main activity
        subprocess.run(["adb", "shell", "am", "start", "-n",
                        "com.pythonnative.android_template/.MainActivity"],
                       check=True)


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
