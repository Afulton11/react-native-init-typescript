# react-native-init-typescript
A python script that can be run to build a react-native project with typescript.

# Installation

1. `git clone https://github.com/Afulton11/react-native-init-typescript.git`
2. `chmod +x react-native-init-typescript/react-native-init-typescript`

3. Add the *react-native-init-typescript* folder to your PATH environment variable.
4. Completely reload your shell
5. Test that it has been installed by running: `react-native-init-typescript --help`

# Usage
To create a react-native project with typescript called Awesome app, just run:
`
react-native-init-typescript AwesomeApp
`

This creates the react-native project, installs needed typescript dependencies, and sets up typescript.

For more info run: `react-native-init-typescript --help`

To run the newly created app on ios or android simply run:
`npm run start:ios`, or `npm run start:android` respectively.

Dont worry, react-native's live reload feature still works amazingly.
