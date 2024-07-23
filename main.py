"""
This script is the entry point for the convert2CAS tool.

It handles the command-line argument parsing and invokes the appropriate
conversion functions from convert.py.

Functions:

main()
"""

import argparse
import os
from converter import get_annotation_types, json_to_cas_converter, cas_to_json_converter


DOCUMENT_PATH = "doc.txt"
TYPESYSTEM_PATH = "typesystem.xml"
OUTPUT_PATH = "output"
EXPORT_DOCUMENT_PATH = "inception_export.txt"
IMPORT_DOCUMENT_PATH = "inception_import"

SPAN_TYPE = "custom.Span"
RELATION_TYPE = "custom.Relation"
SENTENCE_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
TOKEN_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"


def main():
    """
    Based on the provided arguments, calls one of the two conversion modes.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset', default=DOCUMENT_PATH,
            help='Path to the input dataset file.')

    parser.add_argument('--output', default=OUTPUT_PATH,
            help='Path where the output file will be saved. (Also choose the format .json/.xmi)')

    parser.add_argument('--cas_file',
            help='Path to the input UIMA CAS JSON file.')

    parser.add_argument('--typesystem', default=TYPESYSTEM_PATH,
            help='Path to the UIMA CAS type system.')

    args = parser.parse_args()

    if not (os.path.exists(args.dataset) and os.path.exists(args.typesystem)):
        raise OSError("--typesystem " + args.typesystem +
        ", --dataset " + args.dataset +
        "; are not specified or files do not exist.")

    typesystem_path = args.typesystem
    document_path = args.dataset
    output_path = args.output

    typesystem, span_type, relation_type, sentence_type, token_type = get_annotation_types(
        typesystem_path, SPAN_TYPE, RELATION_TYPE, SENTENCE_TYPE, TOKEN_TYPE
    )

    if args.cas_file:
        if not os.path.exists(args.cas_file) or args.cas_file.split(".")[-1] != "json":
            raise OSError("Input UIMA CAS JSON file do not exist or is not a json")

        input_path = args.cas_file

        cas_to_json_converter(
            typesystem,
            span_type,
            relation_type,
            sentence_type,
            token_type,
            document_path,
            input_path,
            output_path
        )
    else:
        json_to_cas_converter(
            typesystem,
            span_type,
            relation_type,
            sentence_type,
            token_type,
            document_path,
            output_path
        )

if __name__ == "__main__":
    main()
