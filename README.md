# Microgpt: 

## Overview

Microgpt is a specialized chatbot tailored for micro-material analysis. It is designed to perform a variety of functions:

•	Data Acquisition: Conduct searches for open-source datasets like Microlib (https://microlib.io/) on Zenodo (https://zenodo.org/), an interdisciplinary open-access repository, and employ toolkit functions to download these datasets using the links available on the respective web pages.

•	Data Filtering: Engage in the retrieval of dataset metadata. Read the metadata to refine the data in accordance with user specifications. Subsequently, organize the filtered data into a newly created file directory.

•	Data Simulation: Invoke simulation tools for 3D microstructure like Taufactor 2 (https://github.com/openjournals/joss-reviews/issues/5358). Document the simulation outcomes in formats such as CSV. Utilize toolkit functions to facilitate the uploading of findings to cloud-based storage, thereby ensuring ease of access and interaction.

•	Data Analysis: Assess the validity of data, compare various datasets, and based on user requirements, formulate hypotheses and provide recommendations. 

•	Data Visualization: Generate relevant images based on user requirements and data outcomes, assisting users in better understanding the content and distribution of the data.

•	Tool Development and Reutilization: Develop custom tools through programming, specifically designed to cater to the unique needs of users.  As user requirements evolve, continuously adapt and enhance these tools, ensuring their applicability and effectiveness in future applications.


## Quick Start Guide

### 1. Environment Setup
Create and activate the Microgpt environment using the following commands in your terminal:

```
conda create --name microgpt python=3.11
conda activate microgpt
```

Create a environment.yml file in the root directory and add:
```plaintext
name: microgpt
channels:
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
      - -r requirements.txt
variables:
  OPENAI_API_KEY: <your-openai-api-key>
  ZENODO_API_KEY: <your-zenodo-api-key>
```

### 2. API Configuration for OpenAI and Zenodo

Replace &lt;your-openai-api-key&gt; and &lt;your-zenodo-api-key&gt; with your actual API keys in environment.yml file.

Update the conda environment using the following commands in your terminal:
```
conda env update -f environment.yml --prune
```

### 3. Optional: Google Cloud Setup
Obtain credentials.json for cloud uploads (optional).

### 4. Execution
Run Microgpt by sourcing the environment variables from .env and executing the main script:

```
python run_assistant.py
```


## Microgpt Example Prompts:
### Data Collection
"Can you search for the Microlib online, which is a dataset of 3D microstructures?"

### Custom Tool Creation and Reuse
"Please write and execute a script to unzip the file ’./microlibDataset.zip"

### Data Filter
"In the ’microlibDataset.zip’ file, can you filter the 3D images related to cast iron?"

### Data Simulation
"Could you analyze the 3D images in the ’./data’ folder to determine their tortuosity, diffusion
factor, volume fraction, and surface area?" 

### Data Analysis
"Read the data in ./data_0.csv, compare microstructure 393, 368, and 365"
"Which microstructure is more suitable to be used as a filter and catalyst carrier?"

### Data Visulization
"Can you generate some figures to create visualizations for the data?  Histograms for each numerical column to understand the distribution of values.  Scatter plots to explore relationships between pairs of numerical variables (e.g., Effective Diffusivity vs.  Tortuosity)"

Input "quit" for ending the conversation
