# RegulusProject

This repository is created for the development of the Regulus AI project

# Node and npm installation

The first and the most essential step in being able to run this project locally is installation of node.js and npm. They are necessary to initiate the react application. The versions used in this repository are -
node.js=v22.2.0 and npm=10.7.0. The link for downloading it is following -  https://nodejs.org/en/download/prebuilt-installer.

After installation make sure that both of them are correct versions using. In order to do it, run in the terminal or command line - `node -v` and `npm -v`.

# Installation of all the dependencies

After both node and npm are ready to work, it means that we have nearly everything to make sure that npm is installed.

This project is divided in two pieces - backend and fronted (regulus-app). So all the further operations need to be implemented after being sure that you are in the correct folder. Therefore, run `cd regulus-app` in your terminal. After that, run `npm install`, so that you are gathering internally all the dependencies used in the project.

You now should be able to navigate to files in the following location - the regulus-app/src/components, where the pages of the web application are saved. Check if all the important modules are successfully installed and no mistakes are displayed. If you still see, that some dependencies are not installed, please use `npm install dependency-name`.

# Running the web page locally

Finally, run `npm start`  in the terminal from the regulus app folder (if you are outside of it, run `cd regulus-app` again) to start the local server with the Regulus AI page.