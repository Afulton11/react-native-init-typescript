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
import re
import argparse
import subprocess
from shutil import copy2, rmtree
from distutils.dir_util import copy_tree
from lazyme.string import color_print

################################################
## These Constants are the script's settings. ##
################################################

#This is the project name text inside of the resources/index.android.tsx and index.ios.tsx
PROJECT_NAME_TEXT = "[project-name]"

DEFAULT_JS_LOC = "index"
TS_JS_INDEX_LOC = "artifacts/index"
TS_INDEX_LOC = "src/index"
TS_INDEX_REGISTRY_REGEX = r'\(\'(\[project-name\])\','

IOS_DIR = "ios/"
IOS_APPDELEGATEM = "AppDelegate.m"

ANDROID_DIR = "android/app/"
ANDROID_GRADLE_DIR = ANDROID_DIR + "build.gradle"
ANDROID_JAVA_DIR = ANDROID_DIR + "src/main/java/com"
ANDROID_MAINAPPLICATION = "MainApplication.java"

ANDROID_GRADLE_REGEX = r'(\n)apply from:\s"..\/..\/node_modules\/react-native\/react.gradle"'
ANDROID_GRADLE_LINES = [
    "",
    "project.ext.react = [",
    "\tentryFile: \"" + TS_JS_INDEX_LOC + ".android.js\"",
    "]",
    ""
]

ANBDROID_MAIN_APP_REGEX = r'new\sReactNativeHost\(.+\)\s{\n()'
ANDROID_MAIN_APP_LINES = [
    ""
    "\t@Override",
    "\tprotected String getJsMainModuleName() {",
    "\t\treturn \"" + TS_JS_INDEX_LOC +".android\"",
    "\t}",
    ""
]

IOS_APPDELEGATEM_REGEX = r'"(' + DEFAULT_JS_LOC + ".ios" + r')"'
IOS_APPDELEGATEM_REPLACEMENT = TS_JS_INDEX_LOC + ".ios"

##Package.json settings
PACKAGE_SCRIPTS_REGEX = r'"scripts":\s+{\n(\s+"start".+\n\s+"test".+\n)\s+},'
PACKAGE_SCRIPTS_LINES = [
    '\t\t"test": "jest --coverage",',
    '\t\t"tsc": "tsc",',
    '\t\t"clean": "rimraf artifacts",',
    '\t\t"build": "npm run clean && npm run tsc --",',
    '\t\t"lint": "tslint src/**/*.ts",',
    '\t\t"watch": "npm run build -- -w",',
    "\t\t\"start:ios\": \"npm run build && concurrently -r 'npm run watch' 'react-native " +
    "run-ios'\",",
    "\t\t\"start:android\": \"npm run build && concurrently -r 'npm run watch' 'react-native " +
    "run-android'\",",
    "\t\t\"start\": \"node node_modules/react-native/local-cli/cli.js start\""
]

PACKAGE_JEST_REGEX = r'"jest":\s+{\n(.+)\s+}'
PACKAGE_JEST_LINES = [
    '\t"preset": "react-native",',
    '\t\t"testRegex": "artifacts/.+\\\\\\\\.(test|spec).js$",',
    '\t\t"coverageDirectory": "coverage",',
    '\t\t"coverageReporters": [',
    '\t\t\t"text-summary",',
    '\t\t\t"html"',
    '\t\t],',
    '\t\t"collectCoverageFrom": [',
    '\t\t\t"artifacts/**/*.js",',
    '\t\t\t"!artifacts/**/*.spec.js",',
    '\t\t\t"!artifacts/**/*.index.js"',
    '\t\t]'
]

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

def lines_to_string(lines):
    """
    returns the given lines to a string of text.
    """
    return '\n'.join(lines)

def read_file_lines(file_path):
    """
    Reads the file_path file in as an array of lines.
    """
    if os.path.exists(file_path):
        file_reader = open(file_path, "r")
        file_contents = file_reader.readlines()
        file_reader.flush()
        file_reader.close()
        return file_contents
    else:
        print_error("File Not Found! " + file_path)
        exit(1)

def read_file_to_string(file_path):
    """
    Reads the file_path file in as a single string.
    """
    return ''.join(read_file_lines(file_path))

def save_file(file_path, file_contents):
    """
    Saves the file_contents to the file_path
    @param file_contents the contents of the file as a single string.
    """
    file_writer = open(file_path, "w")
    file_writer.write(file_contents)
    file_writer.flush()
    file_writer.close()

def save_file_lines(file_path, lines):
    """
    Erases contents of file in file_path and
    writes all lines to the file.
    """
    file_writer = open(file_path, "w")
    file_contents = lines_to_string(lines)
    file_writer.write(file_contents)
    file_writer.flush()
    file_writer.close()

def replace_with_value(string, regex, value):
    """
    replaces the first match's first group with the given value.
    @param string the string to search using the regex
    @param regex the regex containing atleast 1 group.
    @param value the value to replace the matched group with
    """
    matches = re.search(regex, string)
    start_index = matches.start(1)
    end_index = matches.end(1)
    return string[:start_index] + value + string[end_index:]


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
        self.__update_index_registries()
        self.__update_entry_file_paths()
        self.__update_package_json()
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
        if not os.path.exists(src_dst_dir):
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

    def __update_index_registries(self):
        """
        updates the index file registry names with the project name.
        """
        #Handle IOS Index
        self.__update_index_registry("ios.tsx")
        #Handle Android Index
        self.__update_index_registry("android.tsx")

    def __update_index_registry(self, extension):
        """
        Updates the Typescript index file's registry name with the project name.
        @param the index extension: 'android.tsx' or 'ios.tsx'
        """
        index = self.getwd_resource(TS_INDEX_LOC + '.' + extension)
        index_contents = read_file_to_string(index)

        index_contents = replace_with_value(
            index_contents,
            TS_INDEX_REGISTRY_REGEX,
            self.get_name()
        )

        save_file(index, index_contents)

    def __update_entry_file_paths(self):
        """
        Updates the entry file paths for both ios and android.
        """
        print "Updating entry file paths..."
        # Handle iOS entry file paths
        appdelegate_m = self.getwd_resource(
            os.path.join(IOS_DIR, self.get_name(), IOS_APPDELEGATEM)
        )
        appdelegate_m_contents = read_file_to_string(appdelegate_m)

        appdelegate_m_contents = replace_with_value(
            appdelegate_m_contents,
            IOS_APPDELEGATEM_REGEX,
            IOS_APPDELEGATEM_REPLACEMENT
        )
        save_file(appdelegate_m, appdelegate_m_contents)

        #Handle android entry file paths
        build_gradle = self.getwd_resource(ANDROID_GRADLE_DIR)
        main_app_java = self.getwd_resource(
            os.path.join(ANDROID_JAVA_DIR, self.get_name(), ANDROID_MAINAPPLICATION)
        )

        build_gradle_contents = read_file_to_string(build_gradle)
        build_gradle_contents = replace_with_value(
            build_gradle_contents,
            ANDROID_GRADLE_REGEX,
            lines_to_string(ANDROID_GRADLE_LINES)
        )
        save_file(build_gradle, build_gradle_contents)

        main_app_java_contents = read_file_to_string(main_app_java)
        main_app_java_contents = replace_with_value(
            main_app_java_contents,
            ANBDROID_MAIN_APP_REGEX,
            lines_to_string(ANDROID_MAIN_APP_LINES)
        )
        save_file(main_app_java, main_app_java_contents)


    def __update_package_json(self):
        """
        Adds typescript scripts to the project's package.json
        These scripts are used to run/test the RN project.
        Also, this
        Adds the jest testing preset to the project's package.json
        This allows the user to run tests using jest.
        """
        package_json = self.getwd_resource("package.json")
        package_json_contents = read_file_to_string(package_json)

        #Handle package.json scripts:
        print "Adding TypeScript scripts to package.json..."
        package_json_contents = replace_with_value(
            package_json_contents,
            PACKAGE_SCRIPTS_REGEX,
            lines_to_string(PACKAGE_SCRIPTS_LINES)
        )

        #Handle package.json jest testing preset:
        print "Adding TypeScript jest presets to package.json..."
        package_json_contents = replace_with_value(
            package_json_contents,
            PACKAGE_JEST_REGEX,
            lines_to_string(PACKAGE_JEST_LINES)
        )

        #finally, save the final package.json file contents.
        save_file(package_json, package_json_contents)


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
        self.__safe_remove_tree("__tests__/")
        self.__safe_remove(".flowconfig")
        self.__safe_remove("index.android.js")
        self.__safe_remove("index.ios.js")

    def __safe_remove(self, filename):
        """
        Safely removes a Project resource file by checking that it first exists
        before attempting to remove it.
        @param filename the file inside this project's working directory to be removed
        """
        file_path = self.getwd_resource(filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def __safe_remove_tree(self, directory):
        """
        Safely removes a Project resource folder by checking that it first
        exists before attempting to remove it.
        @parm directory the directory to remove inside this projet's working directory
        """
        directory_path = self.getwd_resource(directory)
        if os.path.exists(directory_path):
            rmtree(directory_path)


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
