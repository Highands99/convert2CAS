# Conver2CAS
A software tool designed to convert **annotated sentence datasets** (head-tail-relation) into **UIMA CAS XMI/JSON** format and vice versa. It facilitates the import and export of files in **text annotation tools** like [INCEpTION](https://github.com/inception-project/inception).

## Table of Contents
- [Installation](#installation)
- [Datatset format](#dataset-format)
- [Usage](#usage)

## Installation
Clone the repository and install the necessary dependencies. In the example, pipenv is used, but you can use any tool you prefer.

    # Clone the repository
    git clone https://github.com/Highands99/convert2CAS
    cd convert2CAS

    # Install pipenv if you haven't already
    pip install pipenv

    # Install dependencies
    pipenv install -r requirements.txt

    # Activate the virtual environment
    pipenv shell

## Dataset format
The input dataset file should be a text file **where each line is an annotated sentence** represented as a JSON dictionary. Each dictionary must contain the following fields:

- **token**: A list of tokens (words) in the sentence. Alternatively, the field can be text, which is a single string containing the entire sentence

- **h**/**t**: A dictionary representing the head entity, containing:
    - id: The identifier of the head entity.
    - name: The name of the head entity.
    - pos: The position (start and end indices) of the head entity in the token list or text string.

- **relation**: The type of relation

### Example entry (must be on a single line)
    {"token": ["It", "is", "under", "the", "administration", "of", "Haixi", "Mongol", "and", "Tibetan", "Autonomous", "Prefecture", ".The", "Huatugou", "Airport", "is", "located", "in", "Mangnai", "."],
    "h": {"name": "huatugou airport", "id": "Q3207552", "pos": [13, 15]},
    "t": {"name": "mangnai", "id": "Q1201941", "pos": [18, 19]}, 
    "relation": "place served by transport hub"}

## Usage
Before start you shoud have a dataset file and a typesystem file.

For an example dataset, you can refer to [this repo](https://github.com/dair-iitd/DSRE). 

The typesystem file must be exported from the text annotation tool you are using for the conversion, INCEpTION for example:
1) Go to the Layers tab on the project Settings page.
2) Press the Export button in the Layer Details section.
3) Select UIMA and click Download to save the type system.

The software operates in two modes:

1) Dataset to CAS mode (default): converts the dataset to UIMA CAS and outputs the result in either XMI or JSON format based on the ` --output`  file extension.

2) CAS to Dataset mode: onverts a UIMA CAS JSON (not XMI) file to a dataset format, implicitly activated when the `--cas_file` parameter is provided.

    - **Note** `--dataset` file should be the original dataset from which the `--cas_file` was generated before being imported into a text annotation tool.


### Arguments
- `--typesystem` (default: *typesystem.xmi*): Path to the UIMA CAS XMI type system.

- `--dataset` (default: *doc.txt*): path to the input dataset file.
    
- `--output` (default: *output.json* or *output.txt*): path where the output file will be saved. The format is determined by the file extension (*.json* or *.xmi*).

- `--cas_file`: path to the input UIMA CAS JSON file.

### Examples
If files `doc.txt` and `typesystem.xml` are already present in the same folder as `main.py` and you want to convert `doc.txt` into a new UIMA CAS JSON file called `output.json`, then use the following command:
    
    python main.py

To convert a UIMA CAS json file back into a new dataset file called `output.txt`, use the following command:
    
    python main.py --cas_file inception_export.json
