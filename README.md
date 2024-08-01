# Welcome to ExpEngine of the ExtremeXP framework
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13149489.svg)](https://doi.org/10.5281/zenodo.13149489)
1. [Demo Link](#demo-link)
2. [Introduction](#introduction)
3. [Our Approach](#our-approach)
   - [How It Works](#how-it-works)
4. [Getting Started with ExpEngine](#getting-started-with-expengine)
   - [Setting up the ExpEngine](#setting-up-the-expengine)
   - [Running ExpEngine](#running-expengine)

5. [Setting up the DSL Editor](#setting-up-the-dsl-editor)
   - [Required Software](#required-software)
   - [EXP Language Server](#exp-language-server)
     - [Building the Language Server](#building-the-language-server)
     - [Running the Language Server](#running-the-language-server)
   - [VS Code Extension](#vs-code-extension)
     - [Building the VS Code Extension](#building-the-vs-code-extension)
     - [Running the VS Code Extension](#running-the-vs-code-extension)
     - [Testing the VS Code Extension](#testing-the-vs-code-extension)
   - [Platform-Specific Instructions](#platform-specific-instructions)
     - [Windows](#windows)
     - [Linux](#linux)
     - [macOS](#macos)
7. [Overview and Purpose](#overview-and-purpose)
## Demo Link 

Watch the preliminary demo of ExpEngine [here](https://drive.google.com/file/d/17iwzGjI2TpXRWv63z0l3A3gXPs7_lhgQ/view?usp=sharing).

## Introduction

In the realm of data science and analytics, constructing effective workflows involves navigating through numerous variability points such as different implementations, training algorithms, hyperparameters, and deployment strategies. For data scientists and analysts, the challenge lies in  fine-tuning these workflows to deliver precise and meaningful results that align with user requirements.

To address these complexities, we propose a novel approach centered around user-driven experimentation to optimize data analytics workflows.

## Our Approach

Our approach revolves around a robust tool framework comprising an Experimentation Engine and a Domain-Specific Language (DSL) tailored for workflow optimization. Developed as part of the ExtremeXP EU project, this framework aims to empower data scientists and analysts by streamlining the experimentation process.

To address these complexities, we propose a novel approach centered around user-driven experimentation to optimize data analytics workflows.

### How It Works

1. **Experiment Specification:** The process starts with a data scientist using our DSL editor to create an experiment specification. This specification includes the different options and strategies for the experiment.
   
2. **Execution and Iteration:** The Experimentation Engine reads the specification and sets up multiple workflows based on the specified options. The data scientist can control the experiment by adjusting settings, pausing, resuming, and changing the workflow order as needed.
   
3. **Optimal Workflow Delivery:** At the end of the experiment, the Engine gathers results from all workflows. It identifies the best workflow setup and provides detailed metrics and outputs from the experiment.


## Getting Started with ExpEngine
In the realm of data science and analytics, constructing effective workflows involves navigating through numerous variability points such as different implementations, training algorithms, hyperparameters, and deployment strategies. For data scientists and analysts, the challenge lies in meticulously fine-tuning these workflows to deliver precise and meaningful results that align with user requirements.

### Setting up the ExpEngine

1. **Install Python:**
   - Ensure Python is installed on your system. Recommended version: Python 3.x.

2. **Create a virtual environment:**
   - Set up a Python virtual environment for the ExpEngine to manage dependencies.
     ```bash
     python -m venv env
     source env/bin/activate  # On Windows use `env\Scripts\activate`
     ```

3. **Install textx:**
   - Install the textx library for DSL parsing.
     ```bash
     pip install textx
     ```

4. **Install matplotlib:**
   - Install matplotlib for generating plots (optional but recommended).
     ```bash
     pip install matplotlib
     ```

5. **Install proactive:**
   - Install proactive if it's a required dependency.
     ```bash
     pip install proactive
     ```

6. **Change the proactive credentials in credentials.py:**
   - Update the `credentials.py` file with necessary credentials for proactive usage.


## Running ExpEngine

To run ExpEngine, follow these steps:

1. **Use an IDE**
   - Open your preferred Integrated Development Environment (IDE). This will help you manage your project files and provide a convenient environment for running and debugging your code.

2. **Activate the virtual environment**
   - Before running ExpEngine, ensure that you activate the virtual environment where all the dependencies are installed. This isolates your project's dependencies and ensures compatibility.
   - In your terminal, navigate to your project directory and activate the virtual environment. The command may vary based on your operating system and the tool you used to create the virtual environment:

     On Windows:
     ```sh
     .\venv\Scripts\activate
     ```

     On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

3. **Navigate to the project directory**
   - Change your directory to the `exp-engine` folder where the main script is located:
     ```sh
     cd exp-engine
     ```

4. **Run the ExpEngine script**
   - Execute the main script to start the ExpEngine:
     ```sh
     python exp_engine.py
     ```
     

#### Note:
The datasets and scripts provided with ExpEngine are proprietary. To use your own datasets and task scripts, please upload these materials into the relevant folders within the project directory. Ensure that your datasets and scripts are formatted and organized correctly to integrate smoothly with the ExpEngine framework.

### Setting up the DSL Editor
### Required Software

- [Maven](https://maven.apache.org/)
- [Java](https://www.java.com/en/download/)
- [Node.js](https://nodejs.org/)

### EXP Language Server

#### Building the Language Server

First, you need to create the DSL artifact using Maven. Open your terminal or command prompt and navigate to the `exp.engine.dsl.parent` directory. Then, run the following command:

```bash
cd exp.engine.dsl.parent
mvn install
```

Next, create the language server by navigating to the `exp.engine.dsl.ide` directory and running Maven with the `lang-server` profile:

```bash
cd exp.engine.dsl.parent/exp.engine.dsl.ide
mvn install -Plang-server
```

####  Running the Language Server

After building the language server, navigate to the `target` directory and run the server using the following command:

```bash
cd exp.engine.dsl.parent/exp.engine.dsl.ide/target
java -jar exp.engine.dsl.ide-1.0.0-SNAPSHOT-ls.jar
```

You should see the following message indicating that the language server is running:

```
Welcome to Experiment LSP version 4.0 - Resolved
```

### VS Code Extension

The EXP Language Server can be integrated with VS Code to support `.exp` files.

####  Building the VS Code Extension

First, install the necessary packages by navigating to the `vs-code-ext` directory and running `npm install`:

```bash
cd vs-code-ext
npm install
```

#### Running the VS Code Extension

After installing the packages, build the extension. The generated files will be in the `src/out` directory. Open the `extension.js` script in VS Code:

```bash
code src/out/extension.js
```

Press `F5` to run the extension. This will open a new VS Code window with the extension loaded.

**Note:** Make sure the [language server](#exp-language-server) is running in a separate process.

####  Testing the VS Code Extension

To test the extension, create a new file with the `.exp` extension and write some DSL code. The VS Code extension should provide syntax highlighting, code completion, and other language features for the EXP DSL.

### Platform-Specific Instructions

####  Windows

1. Open Command Prompt or PowerShell.
2. Follow the [Building the Language Server](#building-the-language-server) and [Running the Language Server](#running-the-language-server) steps.
3. For the VS Code extension, open a new Command Prompt or PowerShell window and follow the [Building the VS Code Extension](#building-the-vs-code-extension) and [Running the VS Code Extension](#running-the-vs-code-extension) steps.

####  Linux

1. Open a terminal.
2. Follow the [Building the Language Server](#building-the-language-server) and [Running the Language Server](#running-the-language-server) steps.
3. For the VS Code extension, open a new terminal window and follow the [Building the VS Code Extension](#building-the-vs-code-extension) and [Running the VS Code Extension](#running-the-vs-code-extension) steps.

####  macOS

1. Open a terminal.
2. Follow the [Building the Language Server](#building-the-language-server) and [Running the Language Server](#running-the-language-server) steps.
3. For the VS Code extension, open a new terminal window and follow the [Building the VS Code Extension](#building-the-vs-code-extension) and [Running the VS Code Extension](#running-the-vs-code-extension) steps.

## Overview and Purpose

[//]: # (With the exponential growth of data analytics workflows, optimizing these processes has become increasingly important. Current AutoML tools provide some automation, but there's a need for a more nuanced approach that incorporates various user aspects, such as the expertise of domain experts and data scientists, into the optimization process.)

[//]: # (To address this need, we introduce a comprehensive tool framework consisting of an Experimentation Engine and a Domain-Specific Language &#40;DSL&#41;. This framework allows users not only to define what needs to be optimized but also to specify how the optimization should occur. Users can detail the specific steps involved and the desired level of their involvement, enabling a more tailored and effective optimization process.)

By following these instructions, you should be able to set up and run the ExpEngine, EXP Language Server and VS Code extension on Windows, Linux, and macOS. If you encounter any issues, please refer to the respective documentation for Maven, Java, and Node.js, or seek assistance from the community.
