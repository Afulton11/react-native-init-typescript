#!/usr/bin/env python
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
import fileinput
from shutil import copy2, rmtree
from distutils.dir_util import copy_tree
from lazyme.string import color_print

################################################
## These Constants are the script's settings. ##
################################################

#This is the project name text inside of the resources/index.android.tsx and index.ios.tsx
PROJECT_NAME_TEXT = "[project-name]"

DEFAULT_JS_INDEX_LOC = "index"
TS_JS_INDEX_LOC = "artifacts/index"

IOS_DIR = "ios/"
IOS_APPDELEGATEM = "AppDelegate.m"

ANDROID_DIR = "android/app/"
ANDROID_GRADLE_DIR = ANDROID_DIR + "build.gradle"
ANDROID_JAVA_DIR = ANDROID_DIR + "src/main/java/com"
ANDROID_MAINAPPLICATION = "MainApplication.java"

ANDROID_GRADLE_BEFORE_LINE = "apply from: \"../../node_modules/react-native/react.gradle\""
ANDROID_GRADLE_LINES = [
    "",
    "project.ext.react = [",
    "   entryFile: \"" + TS_JS_INDEX_LOC + ".android.js\"",
    "]",
    ""
]

ANDROID_MAIN_APP_BEFORE_LINE = "  public ReactNativeHost getReactNativeHost() {"
ANDROID_MAIN_APP_LINES = [
    ""
    "@Override",
    "protected String getJsMainModuleName()",
    "   return \"" + TS_JS_INDEX_LOC +".android\"",
    ""
]
ANDROID_MAIN_APP_LINE_OFFSET = 2

IOS_APPDELEGATEM_JS_LOC = DEFAULT_JS_INDEX_LOC + ".ios"
IOS_APPDELEGATEM_REPLACEMENT = TS_JS_INDEX_LOC + ".ios"

def print_exception():
    """
    Prints the most recent exception's info
    """
    print_error(sys.exc_info())

def print_error(error_message):
    """
    Prints the error message in red text using color_print() from lazyme.string
    """
    color_print("ERROR: " + error_message, color="red")

def run_command(entire_command, cwd=os.getcwd()):
    """
    Runs the command.
    @param entire_command the str containing the entire command to run.
    """
    try:
        process = subprocess.Popen(entire_command.split(' '), cwd=cwd)
        process.wait()
    except subprocess.CalledProcessError:
        #Error while executing command
        print_exception()

def get_script_wd():
    """
    returns the current directory of this .py file.
    """
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "resources/"
    )

def get_resource_path(resource_name):
    """
    returns a resource from this script's filepath.
    """
    return os.path.join(get_script_wd(), resource_name)

def read_file_lines(file_path):
    """
    Reads the file_path file in
    """
    if os.path.exists(file_path):
        file_reader = open(file_path, "r")
        file_contents = file_reader.readlines()
        return file_contents
    else:
        print_error("File Not Found! " + file_path)
        exit(1)

def save_file_lines(file_path, lines):
    """
    Erases contents of file in file_path and
    writes all lines to the file.
    """
    file_writer = open(file_path, "w")
    file_contents = "".join(lines)
    file_writer.write(file_contents)
    file_writer.flush()
    file_writer.close()

def replace_file_text(file_path, text_to_replace, replacement_text, first_occurrence=True):
    """
    Searches a file for text_to_replace, and replaces the text with the replacement_text.
    @param first_occurrence whether or not to replace only the first occurrence of text_to_replace.
    """
    lines = read_file_lines(file_path)
    for line in lines:
        if text_to_replace in line:
            line = str(line).replace(text_to_replace, replacement_text)
            if first_occurrence:
                break
    fileinput.close()

def insert_lines_before_line(file_path, before_line, lines, before_line_offset=1):
    """
    Inserts the lines before the before_line in the given file.
    @param before_line the str containing the exact contents of the file line.all
    """
    file_lines = read_file_lines(file_path)
    before_line_index = 0
    for line in lines:
        if line == before_line:
            break
        before_line_index += 1

    file_lines.insert(before_line_index - before_line_offset, lines)



class Project(object):
    """
    This Class Represents a react-native Project.
    """

    def __init__(self, name, path):
        self.__name = name
        self.__path = path
        self.__wd = os.path.normpath(os.path.join(self.__path, self.__name))

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

    def __create(self):
        """
        Creates the react-native project
        """
        print "Creating react-native project..."
        run_command("react-native init " + self.get_name(), self.get_path())

    def __install_typescript_packages(self):
        """
        Installs all necessary typescript developer packages into the project folder.
        npm install
            typescript
            typings
            tslint
            rimraf
            concurrently
            @types/react@latest
            @types/react-native@latest
            @types/jest@latest
        --save-dev
        """
        print "Installing TypeScript dev packages..."
        if os.path.exists(self.getwd()):
            run_command(
                "npm install typescript typings tslint rimraf concurrently" +
                " @types/react@latest @types/react-native@latest @types/jest@latest" +
                " --save-dev",
                self.getwd()
            )
        else:
            print_error("Project Working Directory doesn't exist!")
            print_error("\t" + self.getwd())
            exit(1)

    def __import_typescript_files(self):
        """
        Imports all files that will be used by typescript into the react-native
        project folder. This includes the following:
            tsconfig.json
            tslint.json
            .vscode/tasks.json
        """
        print "Importing TypeScript files..."
        ts_config = get_resource_path("tsconfig.json")
        ts_lint = get_resource_path("tslint.json")
        src_dir = get_resource_path("src/")
        copy2(ts_config, self.getwd())
        copy2(ts_lint, self.getwd())

        #Make the src/ destination folder.
        src_dst_dir = os.path.join(self.getwd(), "src/")
        os.mkdir(src_dst_dir)

        copy_tree(src_dir, src_dst_dir)

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
        vscode = get_resource_path(".vscode/")
        vscode_dst = os.path.join(self.getwd(), ".vscode/")
        copy_tree(vscode, vscode_dst)

    def __update_entry_file_paths(self):
        """
        Updates the entry file paths for both ios and android.
        """
        print "Updating entry file paths..."
        # Handle iOS entry file paths
        appdelegate_m = self.getwd_resource(
            os.path.join(IOS_DIR, self.get_name(), IOS_APPDELEGATEM)
        )
        replace_file_text(
            appdelegate_m,
            IOS_APPDELEGATEM_JS_LOC,
            IOS_APPDELEGATEM_REPLACEMENT
        )

        #Handle android entry file paths
        build_gradle = self.getwd_resource(ANDROID_GRADLE_DIR)
        main_app_java = self.getwd_resource(
            os.path.join(ANDROID_JAVA_DIR, self.get_name(), ANDROID_MAINAPPLICATION)
        )
        insert_lines_before_line(
            build_gradle,
            ANDROID_GRADLE_BEFORE_LINE,
            ANDROID_GRADLE_LINES
        )
        insert_lines_before_line(
            main_app_java,
            ANDROID_MAIN_APP_BEFORE_LINE,
            ANDROID_MAIN_APP_LINES,
            ANDROID_MAIN_APP_LINE_OFFSET
        )

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
        tests_path = self.getwd_resource("__tests__/")
        flow_config = self.getwd_resource(".flowconfig")
        android_index = self.getwd_resource("index.android.js")
        ios_index = self.getwd_resource("index.ios.js")
        rmtree(tests_path)
        os.remove(flow_config)
        os.remove(android_index)
        os.remove(ios_index)

    def get_name(self):
        """
        returns this project's name.
        """
        return self.__name

    def get_path(self):
        """
        returns this project's path, excluding the base folder name.
        """
        return self.__path

    def getwd(self):
        """
        returns this project's working directory.
        """
        return self.__wd

    def getwd_resource(self, resource_name):
        """
        returns the path of a file, or directory, inside of this Project's working directory.
        """
        return os.path.join(self.getwd(), resource_name)

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
        help="The directory the RN typescript project will be created in.",
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
