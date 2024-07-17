from cassis import Cas, load_typesystem, load_cas_from_json
import json


def get_position_offset(tokens_pos, span_pos):
    # Get the character offsets for a span based on token positions
    begin = tokens_pos[span_pos[0]][0]
    end = tokens_pos[span_pos[1]-1][1]
    return [begin, end]


def is_tokenized(json_line):
    # Check if the JSON line is tokenized based on the presence of 'token' key
    if not json_line:
        raise ValueError("File line is empty")

    if "token" in json_line:
        return True
    elif "text" in json_line:
        return False
    else:
        raise ValueError("Neither 'token' nor 'text' key found")


def json_parser_text(json_line):
    # Parse a JSON line that is not tokenized
    sofa = json_line["text"]
    head = json_line["h"]
    tail = json_line["t"]
    relation = json_line["relation"]

    return sofa, head, tail, relation, []


def json_parser_tokens(json_line):
    # Parse a JSON line that is tokenized
    tokens = json_line["token"]
    head = json_line["h"]
    tail = json_line["t"]
    relation = json_line["relation"]

    tokens_pos = []

    tokens_offset = 0
    sofa = ""

    for tokens_count, token in enumerate(tokens, start=1):
        len_token = len(token)
        sofa += " " + token  # Add token to the sofa string

        tokens_pos.append([tokens_offset, tokens_offset + len_token])

        tokens_offset += len_token + 1

    # Update head and tail positions based on token offsets
    head["pos"] = get_position_offset(tokens_pos, head["pos"])
    tail["pos"] = get_position_offset(tokens_pos, tail["pos"])

    return sofa.strip(), head, tail, relation, tokens_pos


def create_span_annotation(span_info, Span, offset=0):
    # Create a span annotation for the CAS
    return Span(
        begin=span_info["pos"][0] + offset,
        end=span_info["pos"][1] + offset,
        label=span_info["id"],
    )


def create_relation_annotation(relation_info, cas_span_head, cas_span_tail, Relation):
    # Create a relation annotation for the CAS
    return Relation(
        begin=cas_span_tail.begin,
        end=cas_span_tail.end,
        Dependent=cas_span_tail,
        Governor=cas_span_head,
        label=relation_info
    )


def create_tokens_annotation(tokens_pos, Token, offset=0):
    # Create token annotations for the CAS
    cas_tokens = []
    for token in tokens_pos:
        cas_token = Token(
            begin=token[0] + offset,
            end=token[1] + offset
        )
        cas_tokens.append(cas_token)
    return cas_tokens


def create_sentence_annotation(sofa_len, Sentence, offset=0):
    # Create a sentence annotation for the CAS
    return Sentence(
        begin=offset,
        end=sofa_len + offset,
    )


class LineConverter():
    def __init__(self, original_line, cas_sentence, cas_relation, cas_head, cas_tail):
        # Initialize LineConverter with provided CAS annotations
        self.original_line = original_line
        self.relation = cas_relation.label
        self.head = LineConverter.__cas_span_parser(cas_head, cas_sentence)
        self.tail = LineConverter.__cas_span_parser(cas_tail, cas_sentence)

    def get_converted_line(self):
        # Return the line with updated head, tail, and relation information
        line = self.original_line
        line["h"] = self.head
        line["t"] = self.tail
        line["relation"] = self.relation
        return line
    
    def get_line_changes(self):
        # Identify changes between the original line and the converted line
        changes = {}

        if self.original_line["h"] != self.head:
            changes.update({"h": [self.original_line["h"], self.head]})

        if self.original_line["t"] != self.tail:
            changes.update({"t": [self.original_line["t"], self.tail]})
        
        if self.original_line["relation"] != self.relation:
            changes.update({"relation": [self.original_line["relation"], self.relation]})

        return changes

    @staticmethod
    def __cas_span_parser(span, sentence):
        # Convert a CAS span into a dictionary format
        span_id = span.label
        span_name = span.get_covered_text()
        span_begin_pos = span.begin - sentence.begin
        span_end_pos = span.end - sentence.begin
        span_pos = [span_begin_pos, span_end_pos]

        return {"id": span_id, "name": span_name, "pos": span_pos}


class TokenizedLineConverter(LineConverter):
    def __init__(self, original_line, cas_sentence, cas_relation, cas_head, cas_tail):
        # Initialize TokenizedLineConverter with provided CAS annotations
        super().__init__(original_line, cas_sentence, cas_relation, cas_head, cas_tail)

        # Adapt positions for tokenized lines
        self.head["pos"] = TokenizedLineConverter.__pos_adapter(cas_head, original_line)
        self.tail["pos"] = TokenizedLineConverter.__pos_adapter(cas_tail, original_line)
    
    @staticmethod
    def __pos_adapter(span, original_line):
        # Convert CAS span positions to token indices
        doc_tokens = original_line["token"]
        span_text = span.get_covered_text()
        span_tokens = span_text.split()

        begin = doc_tokens.index(span_tokens[0])
        end = doc_tokens.index(span_tokens[-1]) + 1

        return [begin, end]


def get_annotation_types(typesystem_path, span_type, relation_type, sentence_type, token_type):
    # Load the UIMA typesystem and get specific annotation types
    with open(typesystem_path, "rb") as ts_file:
        Typesystem = load_typesystem(ts_file)
        Span = Typesystem.get_type(span_type)
        Relation = Typesystem.get_type(relation_type)
        Sentence = Typesystem.get_type(sentence_type)
        Token = Typesystem.get_type(token_type)

    return Typesystem, Span, Relation, Sentence, Token


def json_to_cas_converter(Typesystem, Span, Relation, Sentence, Token, document_path, output_path):
    # Convert a JSON file to a UIMA CAS format
    cas = Cas(typesystem=Typesystem)
    cas.sofa_string = ""

    with open(document_path, 'r') as doc_file:
        first_line = doc_file.readline().strip()
        json_line = json.loads(first_line)

        # Determine the parser function based on tokenization
        if is_tokenized(json_line):
            json_parser = json_parser_tokens
        else:
            json_parser = json_parser_text

        doc_file.seek(0)

        for line_number, line in enumerate(doc_file, start=1):
            line = line.strip()
            if not line: continue

            offset = len(cas.sofa_string)

            json_line = json.loads(line)

            sofa, head_info, tail_info, relation_info, tokens_pos = json_parser(json_line)

            # Create CAS annotations
            cas_span_head = create_span_annotation(head_info, Span, offset)
            cas_span_tail = create_span_annotation(tail_info, Span, offset)
            cas_relation = create_relation_annotation(relation_info, cas_span_head, cas_span_tail, Relation)
            cas_sentence = create_sentence_annotation(len(sofa), Sentence, offset)
            annotations = create_tokens_annotation(tokens_pos, Token, offset)
            annotations.append(cas_span_head)
            annotations.append(cas_span_tail)
            annotations.append(cas_relation)
            annotations.append(cas_sentence)
            
            # Update the CAS with annotations
            cas.sofa_string += sofa + " "
            for annotation in annotations:
                cas.add(annotation)

    # Save the CAS to the specified format
    output_format = output_path.split(".")[-1]
    if output_format == "xmi":
        cas.to_xmi(output_path)
    elif output_format == "json":
        cas.to_json(output_path)
    else:
        cas.to_json(output_path + ".json")


def cas_to_json_converter(Typesystem, Span, Relation, Sentence, Token, document_path, input_path, output_path):
    # Convert a UIMA CAS file to JSON format
    with open(input_path, 'rb') as cas_file:
        cas = load_cas_from_json(cas_file)

    sentences = cas.select(Sentence)
    sentences.sort(key=lambda sentence: sentence.begin)

    # Ensure the output file has a .txt extension
    if output_path.split(".")[-1] != "txt":
        output_path += ".txt"
    
    with open(document_path, 'r', encoding='utf-8') as doc_file, open(output_path, 'w', encoding='utf-8') as exp_file:
        first_line = doc_file.readline().strip()
        json_line = json.loads(first_line)

        # Determine the converter class based on tokenization
        if is_tokenized(json_line):
            Converter = TokenizedLineConverter
        else:
            Converter = LineConverter

        doc_file.seek(0)

        for line_number, doc_line in enumerate(doc_file, start=1):
            doc_line = doc_line.strip()
            sentence = sentences[line_number-1]

            if not doc_line or not sentence: continue

            json_doc_line = json.loads(doc_line)
            cas_relation = cas.select_covered(Relation, sentence)[0]
            cas_head = cas_relation.Governor
            cas_tail = cas_relation.Dependent 

            # Convert the line using the appropriate converter
            line_converter = Converter(json_doc_line, sentence, cas_relation, cas_head, cas_tail)
            json_new_line = line_converter.get_converted_line()
            line_changes = line_converter.get_line_changes()

            # If there are changes, log them (this section is currently commented out)
            # if line_changes:
            #     changes.update({line_number: line_changes})
            
            # Write the converted line to the output file
            json.dump(json_new_line, exp_file, ensure_ascii=False)
            exp_file.write("\n")

    # Optionally, log the changes (this section is currently commented out)
    # with open("log.txt", 'w') as log_file:
    #     changes = json.dumps(changes)
    #     json.dump(changes, log_file)
