# Step-To-Nulink Converter

POC ipynb file can be opened in any notebook environment like jupyter notebook or colab. Unnamend1-BodyPad.step is the example step file being used for the generation example

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Docker](#docker)

## Prerequisites

Before you begin, ensure you have the following installed:

- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [FreeCAD](https://www.freecadweb.org/)

## Installation

1. Clone this repository:
   `git clone https://RohitBAxio@bitbucket.org/nuitdevelopers/step-to-nulink-converter.git`

2. Create a Conda environment using the provided environment.yml file:
    `conda env create -f environment.yml`

3. Activate the Conda environment:
   `conda activate StepToNulink`

## Usage

Follow these steps to use the FastAPI application:

1. Run the FastAPI application using uvicorn:
   `uvicorn main:app --reload`

2. Access the FastAPI app at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your web browser or API client.

## Docker

Dockerize your application for easy deployment:

1. Build the Docker image:
   `docker build -t steptonulink`

2. Run the Docker container:
   `docker run -p 8000:8000 steptonulink`

3. Access the FastAPI app:

    -  Open your web browser and navigate to: [http://localhost:8000](http://localhost:8000).
    -  Open FastApI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
    -  Alternatively, you can use an API client like Postman or curl to interact with the API endpoints.(step-to-nulink-converter\Step-To-Nulink Converter.postman_collection.json)
