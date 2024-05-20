import openai
import os
from utils import *
from assistant_client_functions import *
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# Initialize the Assistant1

instructions_microgpt = """You are an assistant to analyze microstructure. Remember:
    1. You can invoke tools for analysing tomographic data.
       For image analysing, please ensure to call the function once for each path name provided.
       Typically, the number of times the function needs to be invoked corresponds directly to the number of path names you have.
    2. After writing the code, always use a function, create_and_execute_python_file, to upload and execute it.
    3. If the user ask for anlysis the all images in a specific folder, please use data_analysis function. If use ask for analysis an image, please use other function.
    4. If the user ask to filter data in a dataset, eg. try to find iron related 3D images in a specific directory, please use data_filter function.
    5. If the user requests to reuse a tool that is included in a Python file, please employ the 'tool_reuse' function
    6. Don't use extract_and_organize_files function when user ask for data filter in a zip folder!!!"""

assistant_name_microgpt = "Micro gpt"
model_name_microgpt = 'gpt-4-1106-preview'

tools_microgpt = [
             {
                "type": "function",
                "function": {
                "name": "tau_factor",
                "description": "Calculate effective diffusivity, tortuosity factors, volume faction and surface area from tomographic data/3D voxel image. The function is only suitable for two-phase images",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "query_img": {"type": "string", "description": "the path of tomographic data/3D voxel image to analyse. \
                                    it always look like './data/microstructure393.tif', without /mnt"},
                    "D_eff_value": {"type": "number", "description": "the effective diffusivity value"},
                    "tau_value": {"type": "number", "description": "the tortuosity factor value"},
                    "volume_fraction_value": {"type": "number", "description": "the volume fraction value"},
                    "surface_area_value": {"type": "number", "description": "the surface area value"},
                    },
                    "required": ["query_img"]
                }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_and_execute_python_file",
                    "description": "Creates a Python script file with the provided code and executes it upon the user's consent. The script is saved with a specified filename, and the user is prompted to allow its execution.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "String containing the code to be included in the script."
                            },
                            "output_filename": {
                                "type": "string",
                                "default": "created_script.py",
                                "description": "Filename for the created Python script. Default is 'created_script.py'."
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            
            {
                "type": "function",
                "function": {
                    "name": "search_zenodo_datasets",
                    "description": "Searches Zenodo for datasets based on a given query and returns the most relevant results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string to find relevant datasets on Zenodo."
                            },
                            "access_token": {
                                "type": "string",
                                "description": "Access token for authenticating with the Zenodo API."
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of search results to return. Default is 10."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_links_and_download_files",
                    "description": "Accesses a specified webpage, finds all links containing the word 'download', and offers to download each file. If confirmed, the function downloads the file, saves it locally, and uploads it to Google Drive.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page_url": {
                                "type": "string",
                                "description": "URL of the web page to search for download links."
                            },
                            "folder_id": {
                                "type": "string",
                                "description": "ID of the Google Drive folder where the file will be uploaded. Default is a predefined folder ID."
                            },
                            "credentials_file": {
                                "type": "string",
                                "description": "Path to the credentials JSON file for Google Drive API. Default is 'credentials.json'."
                            }
                        },
                        "required": ["page_url"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "extract_and_organize_files",
                    "description": "Extracts files from a specified ZIP archive and organizes files with a certain extension into a designated output folder. IMPORTNANT: Don't use the function when user ask for data filter!!!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "zip_file_path": {
                                "type": "string",
                                "description": "Path to the ZIP file to be extracted.it always look like './Microsturcture.zip',  without ./mnt/data"
                            },
                            "output_folder": {
                                "type": "string",
                                "description": "Path to the folder where files with the specified extension will be organized."
                            },
                            "file_extension": {
                                "type": "string",
                                "description": "The file extension of the files to be organized (e.g., 'txt', 'jpg')."
                            }
                        },
                        "required": ["zip_file_path", "output_folder", "file_extension"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads a file and returns its contents based on the file extension. It supports .csv and .py files. For .csv files, it returns a list of lists, each representing a row. For .py files, it returns the file content as a string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to be read. The path look like './example.csv' or './script.py', without ./mnt/data."
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "upload_google_drive",
                    "description": "Uploads a specified file to a designated folder on Google Drive using Google Drive API. Requires OAuth2 credentials for authentication.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "upload_filename": {
                                "type": "string",
                                "description": "The name of the file to be uploaded."
                            },
                            "folder_id": {
                                "type": "string",
                                "description": "The ID of the Google Drive folder where the file will be uploaded. Default is '18rx0j7qYvW_5Hhyu84alYhcQdWLqRXRa'.",
                                "default": "18rx0j7qYvW_5Hhyu84alYhcQdWLqRXRa"
                            },
                            "credentials_file": {
                                "type": "string",
                                "description": "The path to the JSON file containing OAuth2 credentials for Google Drive API. Default is 'credentials.json'.",
                                "default": "credentials.json"
                            }
                        },
                        "required": ["upload_filename"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "extract_image_paths",
                    "description": "This function extracts the filenames of image files within that directory, particularly those in TIFF format, and compiles these filenames into a list. The function then writes this list to a text file and also creates a descriptive sentence that includes all the extracted image paths. ",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                        "type": "string",
                        "description": "The local directory to search for image files (e.g., './3DvoxelImage')."
                        }
                    },
                    "required": ["directory"]
                    }
                    
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "data_analysis",
                    "description": "This function processes a user query about analyzing 3D images in a specific directory. It uses a GPT-4 model to generate steps for analysis, which includes extracting image filenames, simulating analysis on the images, and storing the results in a CSV file. The function executes these steps and provides a final response based on the analysis.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "user_message": {
                        "type": "string",
                        "description": "The user's query about analyzing 3D images, which will be processed by the GPT-4 model."
                        }
                    },
                    "required": ["user_message"]
                    }

                }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "data_filter",
                        "description": "This function guides the user through a process to filter data (apply certain criteria to find all pieces of data based on specific conditions or attributes) from a dataset based on specific criteria. It outlines steps for confirming the user's request to filter data, using a function to extract metadata from a dataset, and then filtering the data according to the user's criteria. The function utilizes a systematic approach involving user and system messages, and leverages other functions like 'find_json' and 'extract_files_from_folder_or_zip' for data handling.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_message": {
                                    "type": "string",
                                    "description": "The user's message or query related to data filtering."
                                }
                            },
                            "required": ["user_message"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "tool_reuse",
                        "description": "Provides a systematic approach to reuse the tool that created before. It outlines a series of steps to confirm if the user wants to modify and run existing tool code, read the file using read_file function, make necessary code modifications, and finally save and execute the modified code using create_and_execute_python_file function.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_message": {
                                    "type": "string",
                                    "description": "The user's input message which indicates their requirements or queries regarding code modification and execution."
                                }
                            },
                            "required": ["user_message"]
                        }
                    }
                }

                        ]


assistant = create_assistant(assistant_name_microgpt, model_name_microgpt, tools_microgpt, instructions_microgpt,assistant_id_file="assistant_id_microgpt.txt")


# Create a thread
thread = create_thread()

delimiter = "####"
print("\n=========================Welcome to MicroGPT!===========================\n")
print('I am a specialized chatbot tailored for micro-material analysis. I can help you with the following tasks:\n - data collection, filtering, simulation, analysis, visualization, and tool development\n Input quit for ending the conversation\n')
print(f"""Here are some example prompts:\n 
{delimiter} Data Collection
Can you search for the Microlib online, which is a dataset of 3D microstructures?\n

{delimiter} Custom Tool Creation and Reuse
Please write and execute a script to unzip the file \'./microlibDataset.zip\n

{delimiter} Data Filter
In the \'microlibDataset.zip\' file, can you filter all the 3D images related to cast iron?\n

{delimiter} Data Simulation
Could you analyze the 3D images in the \'./data\' folder to determine their tortuosity, diffusion, factor, volume fraction, and surface area?\n

{delimiter} Data Analysis
Read the data in ./data_0.csv, compare microstructure 393, 368, and 365
Which microstructure is more suitable to be used as a filter and catalyst carrier?\n

{delimiter} Data Visulization
Can you generate some figures to create visualizations for the data?  Histograms for each numerical column to understand the distribution of values.  Scatter plots to explore relationships between pairs of numerical variables (e.g., Effective Diffusivity vs.  Tortuosity)\n""")

while True:
    # Get user input
    user_message = input("Enter your message: ")

    # Check if the user wants to quit  
    if user_message.lower() == "quit":
        break

    elif user_message == "ANALYSIS":
        local_directory = './data'
        output_file, prompt = extract_image_paths(local_directory)
        # Send the file path and run the Assistant
        run = send_message_and_run_assistant(thread, assistant, prompt)
        # Poll the run for status updates and handle function calls
        run = poll_run_status(thread, run)

        # Display the final response
        display_final_response(thread, run)

    else:
    # Send a message and run the Assistant
        run = send_message_and_run_assistant(thread, assistant, user_message)
        # Poll the run for status updates and handle function calls
        run = poll_run_status(thread, run)
        # Display the final response
        display_final_response(thread, run)

print(f"Thanks and happy to serve you")
