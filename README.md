# Microgpt: 

## Overview

Microgpt is designed to streamline the process of micro-material analysis through a suite of specialized functionalities. These include data acquisition, filtering, simulation, analysis, visualization, and tool development.

## Features

### Data Acquisition
- **Zenodo Dataset Integration:** Automates retrieval of micro-material datasets from Zenodo's open-access repository.
- **Efficient Downloading:** Utilizes toolkit functionalities for streamlined dataset downloading.

### Data Filtering
- **Metadata Processing:** Employs algorithms for precise metadata extraction and data filtration.
- **Data Organization:** Categorizes and stores processed data methodically.

### Data Simulation
- **3D Microstructure Modeling:** Uses advanced tools for accurate 3D microstructure simulations.
- **Documentation and Cloud Storage:** Ensures detailed recording and cloud uploading of simulation outputs.

### Data Analysis
- **Data Validation:** Implements rigorous methods for ensuring data accuracy.
- **Comparative Analysis and Hypothesis Generation:** Drives analysis and hypothesis development based on user needs.

### Data Visualization
- **Dynamic Image Rendering:** Generates images to elucidate data characteristics.

### Tool Development and Reutilization
- **Custom Tool Creation:** Develops tools tailored to unique analytical requirements.
- **Continuous Tool Enhancement:** Adapts and refines tools for evolving user needs.

## Quick Start Guide

### 1. Environment Setup
Create and activate the Microgpt environment using the following commands in your terminal:

```
conda create --name microgpt python=3.11
conda activate microgpt
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt
```

### 2. API Configuration for OpenAI and Zenodo

Set up API keys for OpenAI and Zenodo. Create a .env file in the root directory and add your API keys:

```plaintext
export OPENAI_API_KEY=<your-openai-api-key>
export ZENODO_API_KEY=<your-zenodo-api-key>
```
Replace <your-openai-api-key> and <your-zenodo-api-key> with your actual API keys.

### 3. Optional: Google Cloud Setup
Obtain credentials.json for cloud uploads (optional).

### 4. Execution
Run Microgpt by sourcing the environment variables from .env and executing the main script:

```
source .env
python run_assistant.py
```


## Microgpt Prompt Examples:
### Data Collection
"Can you search for the Microlib online, which is a dataset of 3D microstructures?"

### Custom Tool Creation and Reuse
"Please write and execute a script to unzip the file ’./microlibDataset.zip"

### Data Filter
"In the ’microlibDataset.zip’ file, can you find all the 3D images related to cast iron?"

### Data Simulation
"Could you analyze the 3D images in the ’./data’ folder to determine their tortuosity, diffusion
factor, volume fraction, and surface area?" 

### Data Analysis
"Read the data in ./data_0.csv, compare microstructure 393, 368, and 365"
"Which microstructure is more suitable to be used as a filter and catalyst carrier?"

### Data Visulization
"Can you generate some figures to create visualizations for the data?  Histograms for each numerical column to understand the distribution of values.  Scatter plots to explore relationships between pairs of numerical variables (e.g., Effective Diffusivity vs.  Tortuosity)"

Input "quit" for ending the conversation