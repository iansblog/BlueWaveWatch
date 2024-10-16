# Project Documentation

This project consists of several important documentation files that provide essential information about the application, its structure, and deployment processes. Below is a brief description of each markdown file available in this repository:
    
## Documentation Files

- **[dockerbuildReadme.md](dockerbuildReadme.md)**  
  A guide on how to build and push the Docker image to Docker Hub. This document contains instructions for maintaining and updating the Docker setup for the application.

- **[codeOverview.md](codeOverview.md)**  
  An overview of the code flow and database structure. This document provides insights into the architecture of the application, including how different components interact with each other.

- **[readme.md](readme.md)**  
  The main project documentation that outlines the purpose of the project, installation instructions, usage details, and other relevant information for users and developers.

For further details, please refer to the respective markdown files.

# Project overview
This is a simple Python/Flask application that can be built from a single project and deployed to the following chip sets:
- linux/amd64
- linux/arm64

This project is being used as a test bed for deployment to cloud hosting and locally on a Raspberry PI 5. 


## Docker commands
### Build and test
docker build -t neonsunset/bluewavewwatch

#### Port 80 (default for the internet)
- docker container run -d -p 80:80 neonsunset/bluewavewwatch:latest 
- To test the port 80 Go to http://localhost

### Build for the Raspbery Pi (pi 5) also. 
- docker buildx build --platform linux/amd64,linux/arm64 -t neonsunset/bluewavewwatch .

### Multi platform build & push to hub 
- docker buildx build --platform linux/amd64,linux/arm64 -t neonsunset/bluewavewwatch . --push

## Local deployment using the docker-compose.yml file
- docker compose up

or runing

- docker stop condescending_kilby
- docker rm condescending_kilby
- docker run -d --name bluewavewwatch --restart always -p 80:80 neonsunset/bluewavewwatch:latest

Please change the port as needed. 

## Docker Hub Location
To see the output on docker hub please go to: 
- [Docker Hub](https://hub.docker.com/r/neonsunset/bluewavewwatch)