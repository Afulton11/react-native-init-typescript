"""
RNTypescript.py

This py script will automatically create a react-native project with typescript, provided
you have both npm and react-native-cli installed.

args: [project-name] [project-dir] [vscode-tasks?]

use --help for more argument info.

Note, Before running make sure the project dir has no folder with the project's name inside of it.

"""
import sys
import os
import argparse
import subprocess

DEFAULT_JS_LOC = "index"
TYPESCRIPT_JS_LOC = "artifacts/index"

ANDROID_GRADLE_LINES = [
    "project.ext.react = [",
    "   entryFile: \"" + TYPESCRIPT_JS_LOC + ".android.js\"",
    "]",
]

ANDROID_MAIN_APP_LINES = [
    "@Override",
    "protected String getJsMainModuleName()",
    "   return \"" + TYPESCRIPT_JS_LOC +".android\""
]

IOS_APPDELEGATEM_JS_LOC = DEFAULT_JS_LOC + ".ios"
IOS_APPDELEGATEM_REPLACEMENT = TYPESCRIPT_JS_LOC + ".ios"

def print_exception():
    """
    Prints the most recent exception's info
    """
    print sys.exc_info()

def run_command(entire_command, cwd=os.getcwd()):
    """
    Runs the command.
    @param entire_command the str containing the entire command to run.
    """
    try:
        subprocess.Popen(entire_command.split(' '), cwd)
    except subprocess.CalledProcessError:
        #Error while executing command
        print_exception()



class Project(object):
    """
    This Class Represents a react-native Project.
    """

    def __init__(self, name, path):
        self.__name = name
        self.__path = path

    def build(self, vscode=False):
        """
        Builds the entire react-native typescript project and installs all required packages.
        """
        print "Building React-native Typescript Project..."
        self.__create()
        self.__install_typescript_packages()
        self.__import_typescript_files()
        self.__update_entry_file_paths()
        self.__add_package_scripts()
        self.__add_typescript_jest()
        self.__delete_unnecessary_files()
        if vscode:
            self.__import_vscode_tasks()

        print "Built React-native Typescript Project!"
        print "You can find it at: " + self.getwd() + "!"
        return None

    def __create(self):
        """
        Creates the react-native project
        """
        print "Creating react-native project..."
        run_command("", )

    def __install_typescript_packages(self):
        """
        Installs all necessary typescript developer packages into the project folder.
        npm install
            typescript
            typings --> Should this be installed globally so you can use the typings command?
            tslint
            rimraf
            concurrently
            @types/react@latest
            @types/react-native@latest
            @types/jest@latest
        --save-dev
        """
        print "Installing TypeScript dev packages..."

    def __import_typescript_files(self):
        """
        Imports all files that will be used by typescript into the react-native
        project folder. This includes the following:
            tsconfig.json
            tslint.json
            .vscode/tasks.json
        """
        print "Importing TypeScript files..."

    def __import_vscode_tasks(self):
        """
        Imports vscode tasks into the react-native typescript project.
        These use the package.json's scripts.
        Here is a list of the tasks:
            start:ios --> Starts the app on ios
            start:android --> Starts the app on android
            runServer --> Starts the js development server
            test --> run tests
            build --> Builds the Typescript project
        """
        print "Importing vscode tasks to the project..."

    def __update_entry_file_paths(self):
        """
        Updates the entry file paths for both ios and android.
        """
        print "Updating entry file paths..."

    def __add_package_scripts(self):
        """
        Adds typescript scripts to the project's package.json
        These scripts are used to run/test the RN project.
        """
        print "Adding TypeScript scripts to package.json..."

    def __add_typescript_jest(self):
        """
        Add the jest testing preset to the project's package.json
        This allows the user to run tests using jest.
        """
        print "Adding TypeScript jest test presets to package.json..."

    def __delete_unnecessary_files(self):
        """
        Deletes unnecessary files that were created during the react-native project creation.
        Files/Folders that aren't needed [it deletes] for the typescript installation:
            index.android.js
            index.ios.js
            __tests__/
            .flowconfig
        """
        print "Removing unnecessary react-native files..."

    def get_name(self):
        """
        returns this project's name.
        """
        return self.__name

    def get_path(self):
        """
        returns this project's path.
        """
        return self.__path

    def getwd(self):
        """
        returns this project's working directory.
        """
        return os.path.normpath(os.path.join(self.__path, self.__name))

try:
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument(
        "project_name",
        help="The Name of the React-native (RN) Typescript project.",
        type=str
    )
    ARG_PARSER.add_argument(
        "project_dir",
        nargs='?',
        help="The directory the RN typescript project will be installed in.",
        default=os.getcwd(),
    )
    ARG_PARSER.add_argument(
        "-vs",
        "--vscode-tasks",
        help="Install vs-code tasks into the react-native project.",
        action='store_true',
    )

    ARGS = ARG_PARSER.parse_args()

    CREATED_PROJECT = Project(ARGS.project_name, ARGS.project_dir)

    CREATED_PROJECT.build(ARGS.vscode_tasks)

except argparse.ArgumentError:
    print_exception()
