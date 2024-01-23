# Microgpt
Microgpt is a specialized chatbot tailored for micro-material analysis.

It is designed to perform a variety of functions:

•	Data Acquisition: Conduct searches for open-source datasets on Zenodo, an interdisciplinary open-access repository, and employ toolkit functions to download these datasets using the links available on the respective web pages.

•	Data Filtering: Engage in the retrieval of dataset metadata. Read the metadata to refine the data in accordance with user specifications. Subsequently, organize the filtered data into a newly created file directory.

•	Data Simulation: Invoke simulation tools for 3D microstructure. Document the simulation outcomes in formats such as CSV. Utilize toolkit functions to facilitate the uploading of findings to cloud-based storage, thereby ensuring ease of access and interaction.

•	Data Analysis: Assess the validity of data, compare various datasets, and based on user requirements, formulate hypotheses and provide recommendations. 

•	Data Visualization: Generate relevant images based on user requirements and data outcomes, assisting users in better understanding the content and distribution of the data.

•	Tool Development and Reutilization: Develop custom tools through programming, specifically designed to cater to the unique needs of users.  As user requirements evolve, continuously adapt and enhance these tools, ensuring their applicability and effectiveness in future applications.


### Quick Start

1. set up environment
terminal:
conda create --name microgpt python=3.11
conda activate microgpt
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt

2. set up openai & zenodo api
create a file .env, 

export OPENAI_API_KEY=
export ZENODO_API_KYE=

3. if hope to upload google cloud 
need apply for credentials.json
no nessaccery if don't want to upload the files to cloud

4. execute
terminal:
source .env
python run_assistant.py

### prompt example:
Data Collection
"Can you search for the Microlib online, which is a dataset of 3D microstructures?"

Custom Tool Creation and Reuse
"Please write and execute a script to unzip the file ’./microlibDataset.zip"

Data Filter
"In the ’microlibDataset.zip’ file, can you find all the 3D images related to cast iron?"

Data Simulation
"Could you analyze the 3D images in the ’./data’ folder to determine their tortuosity, diffusion
factor, volume fraction, and surface area?" 

Data Analysis
"Read the data in ./data_0.csv, compare microstructure 393, 368, and 365"
"Which microstructure is more suitable to be used as a filter and catalyst carrier?"

Data Visulization
"Can you generate some figures to create visualizations for the data?  Histograms for each numerical column to understand the distribution of values.  Scatter plots to explore relationships between pairs of numerical variables (e.g., Effective Diffusivity vs.  Tortuosity)"

"quit" for ending the conversation