import argparse
import os
from converter import get_annotation_types, json_to_cas_converter, cas_to_json_converter

# Constants for default paths and annotation types
DOCUMENT_PATH = "doc.txt"
TYPESYSTEM_PATH = "typesystem.xml"
OUTPUT_PATH = "output"
EXPORT_DOCUMENT_PATH = "inception_export.txt"
IMPORT_DOCUMENT_PATH = "inception_import"

# Annotation types
SPAN_TYPE = "custom.Span"
RELATION_TYPE = "custom.Relation"
SENTENCE_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
TOKEN_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser()

    # Add arguments for dataset, output, cas_file, and typesystem
    parser.add_argument('--dataset', default=DOCUMENT_PATH,
            help='Path to the input dataset file.')

    parser.add_argument('--output', default=OUTPUT_PATH,
            help='Path where the output file will be saved. (Also choose the format .json/.xmi)')

    parser.add_argument('--cas_file', 
            help='Path to the input UIMA CAS JSON file.')

    parser.add_argument('--typesystem', default=TYPESYSTEM_PATH,
            help='Path to the UIMA CAS type system.')
    
    args = parser.parse_args()

    # Check if the dataset and typesystem paths exist
    if not (os.path.exists(args.dataset) and os.path.exists(args.typesystem)):
        raise Exception("--typesystem " + args.typesystem + ", --dataset " + args.dataset + "; are not specified or files do not exist.")

    typesystem_path = args.typesystem
    document_path = args.dataset
    output_path = args.output

    # Get annotation types from the typesystem
    Typesystem, Span, Relation, Sentence, Token = get_annotation_types(
        typesystem_path, SPAN_TYPE, RELATION_TYPE, SENTENCE_TYPE, TOKEN_TYPE
    )

    # If a CAS JSON file is provided, convert CAS to JSON
    if args.cas_file:
        if not os.path.exists(args.cas_file) or args.cas_file.split(".")[-1] != "json":  # Check if the CAS file exists and is a JSON file
            raise Exception("Input UIMA CAS JSON file does not exist or is not a json")

        input_path = args.cas_file

        # Convert CAS to JSON
        cas_to_json_converter(
            Typesystem, Span, Relation, Sentence, Token, document_path, input_path, output_path
        )
    else:
        # Convert JSON to CAS
        json_to_cas_converter(
            Typesystem, Span, Relation, Sentence, Token, document_path, output_path
        )

if __name__ == "__main__":
    main()
