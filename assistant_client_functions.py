import openai
import json
import time
import os
from PIL import Image
import io
import mimetypes
from utils import *
import pandas as pd


# Configure your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY"
client = openai.OpenAI(api_key=openai.api_key)

# Create an Assistant with custom function definitions
def create_assistant(assistant_name=None, model_name=None, tools=None, instructions=None, assistant_id_file="assistant_id_microgpt"):
    # Check if the assistant ID file exists
    if os.path.exists(assistant_id_file):
        # Read the assistant ID from the file
        with open(assistant_id_file, "r") as file:
            assistant_id = file.read().strip()
    else:
        # Create an Assistant with custom functions
        print("Creating an Assistant with custom functions...")
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            model=model_name,
            tools=tools
        )
        assistant_id = assistant.id

        # Write the assistant ID to a file
        with open(assistant_id_file, "w") as file:
            file.write(assistant_id)
        print(f"Assistant created with ID: {assistant_id}")

    # Retrieve the assistant
    assistant = client.beta.assistants.retrieve(assistant_id)
    print(f"Assistant retrieved with ID: {assistant.id}")

    return assistant



# Create a Thread for a new user conversation
def create_thread():
    print("Creating a Thread for a new user conversation...")
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    return thread



# Add a user's message to the Thread and create a Run
def send_message_and_run_assistant(thread, assistant, user_message):
    print(f"Adding user's message to the Thread: '{user_message}'")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    
    print("Running the Assistant to process the message...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    return run



# Poll the Run status and handle function calls
def poll_run_status(thread, run):
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status in ['completed', 'failed', 'cancelled']:
            break
        elif run.status == 'requires_action':
            handle_required_actions(thread, run)
        else:
            print("Waiting for the Assistant to process...")
            time.sleep(5)
    return run

client = openai.Client()
def get_completion(messages, model="gpt-4-1106-preview", 
                temperature=0, max_tokens=500):

    completion = client.chat.completions.create(
        model= model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content

def execute_step(thread, assistant, step):
    run = send_message_and_run_assistant(thread, assistant, step)
    run = poll_run_status(thread, run)
    response = display_final_response(thread, run)
    return response

# Define a function to analyze the images in a directory
def data_analysis(user_message):
    
    delimiter = "####"
    system_message = f"""
    Follow these steps to answer the customer queries.
    The customer query will be delimited with four hashtags,
    i.e. {delimiter}. 

    Step 1:{delimiter} First, determine if the user is asking a question about analyzing 3D images in a specific directory.
          If the user is asking about analyzing 3D images in a specific directory,
              call a function to extract the filenames of images in the directory.

    Step 2:{delimiter} Next, call a simulation function to analyze the images.

    Step 3:{delimiter}:Finally, store all the data in a CSV file.


    Use the following format:
    Step 1:{delimiter} <step 1 reasoning>
    Step 2:{delimiter} <step 2 reasoning>
    Step 3:{delimiter} <step 3 reasoning>

    Make sure to include {delimiter} to separate every step.
    """

    messages =  [  
    {'role':'system', 
    'content': system_message},    
    {'role':'user', 
    'content': f"{delimiter}{user_message}{delimiter}"},  
    ] 

    response = get_completion(messages)

    try:
        steps = response.split("Step ")
        step1 = steps[1].split("####")[1].strip()
        step2 = steps[2].split("####")[1].strip()
        step3 = steps[3].split("####")[1].strip()
        print("=========================Thinking...=======================")
        print("Step 1:", step1)
        print("Step 2:", step2)
        print("Step 3:", step3)
        print("=================Start solving the problem!================")

    except Exception as e:
        final_response = "Sorry, I'm having trouble right now, please try asking another question."
        
    assistant_name_datagpt = "Data gpt"
    model_name_datagpt = 'gpt-4-1106-preview'
    instructions_datagpt = "This assistant will help you to analyse 3D images in a specific directory."
    tools_datagpt = [{"tpye":"code_interpreter"},
                        {"type": "retrieval"},
        
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
                    },
                    "return": {
                    "type": "object",
                    "description": "A tuple containing the path to the output text file with image paths and a sentence listing these paths.",
                    "properties": {
                        "output_file_path": {
                        "type": "string",
                        "description": "The path to the output text file containing the list of image paths."
                        },
                        "prompt": {
                        "type": "string",
                        "description": "A sentence that lists all the extracted image paths."
                        }
                    }
                    }
                }
            }
    ]
    assistant = create_assistant(assistant_name_datagpt, model_name_datagpt, tools_datagpt, instructions_datagpt,assistant_id_file="assistant_id_datagpt.txt")
    thread = create_thread()

    final_message = "have a conclusion of the previous steps and response to user in 3 sentences"
    execute_step(thread, assistant, step1)
    execute_step(thread, assistant, step2)
    execute_step(thread, assistant, step3)
    final_response = execute_step(thread, assistant, final_message)

    return final_response

def data_filter(user_message):
    
    delimiter = "####"
    system_message = f"""
    Follow these steps to answer the customer queries. You have the following function to use:

    The customer query will be delimited with four hashtags,
    i.e. {delimiter}. 

    Step 1:{delimiter} First, confirm whether the user is asking you to filter the data in the database based on their criteria. 
        Determine the directory of the database.
    Step 2:{delimiter} If the user is asking about 
                filter 3D images in a dataset, you have a function called find_json, you can use it to unfold zip file, find the meta data of the dataset in the file and extract the metadata
    Step 3:{delimiter} Now that you have the metadata, which is in a JSON format, focus on the description and keywords within the metadata. Filter all the data in the database that aligns with the user's criteria.adata, and filter all the data in the database which align with the user's criteria.


    Use the following format:
    Step 1:{delimiter} <step 1 reasoning>
    Step 2:{delimiter} <step 2 reasoning>
    Step 3:{delimiter} <step 3 reasoning>

    Make sure to include {delimiter} to separate every step.
    """

    messages =  [  
    {'role':'system', 
    'content': system_message},    
    {'role':'user', 
    'content': f"{delimiter}{user_message}{delimiter}"},  
    ] 

    response = get_completion(messages)
        
    assistant_name_filtergpt = "Filter gpt"
    model_name_filtergpt = 'gpt-4-1106-preview'
    instructions_filtergpt = "This assistant will help you to filter data based on specific criterial in a dataset. You don't need user to upload the dataset file to this platform\
        you can use the given function directly with the dataset file directory.\
            IMPORTANT: the directory always looks like './+filename.zip',  without ./mnt/data"
    tools_datagpt = [{"tpye":"code_interpreter"},
                        {"type": "retrieval"},
        
                {
                    "type": "function",
                    "function": {
                        "name": "find_json",
                        "description": "Unzips a zip file or searches a directory to find metadata files in JSON or XML format. Prompts the user for confirmation before extracting the metadata. Returns the contents of the metadata file or a message if no metadata is found.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_or_dir_path": {
                                    "type": "string",
                                    "description": "The path to the zip file or directory where the metadata search is performed, it is always look like ./+filename, without mnt/data/."
                                }
                            },
                            "required": ["file_or_dir_path"]
                        },
                        "sub_functions": {
                            "is_non_empty_file": {
                                "description": "Checks if a given file path points to a non-empty file."
                            },
                            "search_metadata": {
                                "description": "Searches the given directory for metadata files ending in '.json' or '.xml', asking the user for confirmation before extracting."
                            }
                        },
                        "error_handling": {
                            "description": "Handles JSON decoding errors when reading and parsing JSON files."
                        },
                        "final_output": {
                            "type": "string",
                            "description": "Returns the contents of the extracted metadata file if found and confirmed, or a message indicating no metadata found."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "extract_files_from_folder_or_zip",
                        "description": "Extracts files with a specified name from a given folder or zip file, including any nested folders and zip files within. The function searches for files that match the target filename in the source path, which can be either a directory or a zip file. If found, the files are extracted to a specified destination folder.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "source_path": {
                                    "type": "string",
                                    "description": "Path to the source folder or zip file."
                                },
                                "target_filename": {
                                    "type": "string",
                                    "description": "Name of the file to search for and extract."
                                },
                                "destination_folder": {
                                    "type": "string",
                                    "default": "DATA",
                                    "description": "Folder where the extracted files will be stored. Default is 'DATA'."
                                }
                            },
                            "required": ["source_path", "target_filename"]
                        }
                    }
                }


    ]

    assistant = create_assistant(assistant_name_filtergpt, model_name_filtergpt, tools_datagpt, instructions_filtergpt,assistant_id_file="assistant_id_filtergpt.txt")
    thread = create_thread()

    response1 = execute_step(thread, assistant, "the directory always look like ./+filename.zip, but not mnt/data/+filename:\n"+response)
    user_input = input("Please input an exmaple of data filename:")
    user_message2 = f"The user input an exmaple of data filename {user_input}. Based on the filename example provided by the user, deduce the pattern of filenames of the extracted data.\
        and list all the filenames of extracted data. \
        For instance, if the user inputs an example filename as 'microstructure039.tif', \
        infer that all data filenames in the dataset follow the pattern './microstructureXYZ.tif', where 'XYZ' represents a three-digit number. \
        "
    response2 = execute_step(thread, assistant, user_message2)
    user_message3 = "extract the selected data based on their name from the dataset directory, and store them into DATA folder, with a function called extract_files_from_folder_or_zip"
    response3 = execute_step(thread, assistant, user_message3)

    return response3

def tool_reuse(user_message):
    
    delimiter = "####"
    system_message = f"""
    Follow these steps to answer the customer queries. You have the following function to use:

    The customer query will be delimited with four hashtags,\
    i.e. {delimiter}. 

    Step 1:{delimiter} First, confirm whether the user wants to reuse the tool created before, by modifing the code of a file according to his needs and then run it. If yes, call the read_file function to read this file, specifying the file path clearly \
    Step 2:{delimiter} Now that you have the code, make modifications according to the user's requirements\
    Step 3:{delimiter} Call the create_and_execute_python_file function to save and overwrite the original code, keeping the file name unchanged,clearly specifying the file path to be saved.\

    Use the following format:
    Step 1:{delimiter} <step 1 reasoning>
    Step 2:{delimiter} <step 2 reasoning>
    Step 3:{delimiter} <step 3 reasoning>

    Make sure to include {delimiter} to separate every step.
    """

    messages =  [  
    {'role':'system', 
    'content': system_message},    
    {'role':'user', 
    'content': f"{delimiter}{user_message}{delimiter}"},  
    ] 

    response = get_completion(messages)
        
    assistant_name_toolgpt = "Tool resuse gpt"
    model_name_toolgpt = 'gpt-4-1106-preview'
    instructions_toolgpt = "This is an assistant to reuse the tools. It can modify the code of a file according to user's needs and then run it\
            IMPORTANT: the directory always looks like './+filename.zip',  without ./mnt/data"
    tools_toolgpt = [{"tpye":"code_interpreter"},
                        {"type": "retrieval"},
        
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
            }

    ]

    assistant = create_assistant(assistant_name_toolgpt, model_name_toolgpt, tools_toolgpt, instructions_toolgpt,assistant_id_file="assistant_id_toolgpt.txt")
    thread = create_thread()

    response = execute_step(thread, assistant, response + "in the code you are writing, please make sure the directory always look like ./+filename.zip, but not mnt/data/+filename:\n")

    return response

# Handle the required actions for function calls
def handle_required_actions(thread, run):
    print("Assistant requires function calls...")
    required_actions = run.required_action.submit_tool_outputs
    with open("required_actions.json", "w") as f:
                required_actions_json = required_actions.model_dump()
                json.dump(required_actions_json, f, indent=4)
    tool_outputs = []

    for action in required_actions.tool_calls:
        func_name = action.function.name
        arguments = json.loads(action.function.arguments)
        if func_name == "tau_factor":
            query_img_path = arguments.get("query_img")
            results = tau_factor(query_img_path)

            # Prepare the function response in the expected format
            function_response = {
                "These are the JSON-formatted simulation results of the 3D images": results
            }

        elif func_name == "create_and_execute_python_file":
            code = arguments.get("code")
            output_filename = arguments.get("output_filename", "created_script.py")
            results = create_and_execute_python_file(code, output_filename)
            function_response = {
                "Message": results                                
                }
            
        elif func_name == "search_zenodo_datasets":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 10)
            results = search_zenodo_datasets(query, max_results)
            function_response = {
                "Results": results
            }
        elif func_name == "download_links_and_download_files":
            page_url = arguments.get("page_url")
            results = download_links_and_download_files(page_url)
            function_response = {
                "Message": results
            }
        elif func_name == "extract_and_organize_files":
            zip_file_path = arguments.get("zip_file_path")
            output_folder = arguments.get("output_folder")
            file_extension = arguments.get("file_extension")
            extract_and_organize_files(zip_file_path, output_folder, file_extension)
            function_response = {
                "Message": "Files extracted and organized successfully."
            }
        elif func_name == "read_file":
            file_path = arguments.get("file_path")
            results = read_file(file_path)
            function_response = {
                "Results": results
            }
        elif func_name == "upload_google_drive":
            file_path = arguments.get("upload_filename")
            resutls = upload_google_drive(file_path)
            function_response = {
                "Message": resutls
            }
        elif func_name == "extract_image_paths":
            directory = arguments.get("directory")
            output_file_path, image_path = extract_image_paths(directory)
            function_response = {
                "Image_path": image_path
            }
        elif func_name == "data_analysis":
            user_message = arguments.get("user_message")
            results = data_analysis(user_message)
            function_response = {
                "Message": results
            }
        
        elif func_name == "find_json":
            file_or_dir_path = arguments.get("file_or_dir_path")
            results = find_json(file_or_dir_path)
            function_response = {
                "Message": results
            }

        elif func_name == "extract_files_from_folder_or_zip":
            source_path = arguments.get("source_path")
            target_filename = arguments.get("target_filename")
            extract_files_from_folder_or_zip(source_path, target_filename)
            function_response = {
                "Message": "Files extracted successfully."
            }
        
        elif func_name == "data_filter":
            user_message = arguments.get("user_message")
            results = data_filter(user_message)
            function_response = {
                "Message": results
            }

        elif func_name == "tool_reuse":
            user_message = arguments.get("user_message")
            results = tool_reuse(user_message)
            function_response = {
                "Message": results
            }

        else:
            raise ValueError(f"Unknown function: {func_name}")

        print(f"Function '{func_name}' called with arguments: {arguments}")

        tool_outputs.append({
            "tool_call_id": action.id,
            "output": json.dumps(function_response)
        })

    print("Submitting function call outputs back to the Assistant...")
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )



def display_final_response(thread, run):
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    # save the run steps to a json file
    with open("run_steps.json", "w") as f:
        run_steps_json = run_steps.model_dump()
        json.dump(run_steps_json, f, indent=4)
    # save the messages to a json file
    with open("messages.json", "w") as f:
        messages_json = messages.model_dump()
        json.dump(messages_json, f, indent=4)
    msg = messages.data[0]

    for content in msg.content:
        # skip if content has "image_file" as attribute
        if hasattr(content, "image_file"):
            continue
        # print the text if content has "text" as attribute
        if hasattr(content, "text"):
            print('Response================================')
            print("\033[93m"+f"{msg.role.capitalize()}: {content.text.value}"+"\033[0m")
            print('=====================================END')
    

    # Initialize a list to store updated messages
    updated_messages = []

    image_counter = 0
    data_counter = 0
    # Process each message in the messages list
    for message in messages.data:
        if message.content:
            citations = []
            for content_part in message.content:
                if content_part.type == 'text':
                    annotations = content_part.text.annotations
                    text_value = content_part.text.value
                    for index, annotation in enumerate(annotations):
                        text_value = text_value.replace(annotation.text, f' [{index}]')
                        if (file_citation := getattr(annotation, 'file_citation', None)):
                            cited_file = client.files.retrieve(file_citation.file_id)
                            citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
                        elif (file_path := getattr(annotation, 'file_path', None)):
                            cited_file = client.files.retrieve(file_path.file_id)
                            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                            image_file_id = cited_file.id
                            file_content: bytes = client.files.with_raw_response.retrieve_content(image_file_id).content
                            file_type, _ = mimetypes.guess_type(cited_file.filename)
                            if file_type and file_type.startswith('image/'):
                                # if file is an image, open it with PIL
                                image = Image.open(io.BytesIO(file_content))
                                image.save(f"image_{image_counter}.png")
                                image_counter += 1
                            elif file_type and file_type.startswith('text/csv') or cited_file.filename.endswith('.csv'):
                                # if file is a CSV file, read it into a Pandas DataFrame  
                                csv_file = io.StringIO(file_content.decode())
                                df = pd.read_csv(csv_file)
                                df.to_csv(f"data_{data_counter}.csv", index=False)
                                data_counter += 1
                            else:
                                print(f"Unsupported file type: {file_type}")
                            
                    text_value += '\n' + '\n'.join(citations)
                    content_part.text.value = text_value

                    # might need to fix, if the file is not an image
                elif content_part.type == 'image_file':
                    image_file_id = content_part.image_file.file_id
                    image_data: bytes = client.files.with_raw_response.retrieve_content(image_file_id).content
                    image = Image.open(io.BytesIO(image_data))
                    image.show()
                    # save the image to a file
                    image.save(f"image_{image_counter}.png")
                    image_counter += 1
            updated_messages.append(message)
    # for updated_message in updated_messages:
    #     print(updated_message.content[0].text.value)
            
    return content.text.value

