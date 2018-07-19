from yaksh.pycode_similar import detect
from ast import parse, walk, FunctionDef


def _convert_to_template(candidate_code):
    return "def template():\n    {}".format("\n    ".join(
                                     candidate_code.splitlines())
                                     )

def _get_original_code(templated_code):
    original_code = templated_code.replace("def template():\n", "")
    return original_code


def _format_codes(codes):
    """finds all the codes which don't contain function and adds 
    function to those codes.
    """
    for name, code in codes.items():
        function_present = False
        for node in walk(parse(code)):
            if isinstance(node, FunctionDef):
                function_present = True
                break
        if not function_present:
            codes[name] = _convert_to_template(code)
    return codes

def sort_plagiarised_files(codes, threshold_percent=70):
    """returns plag which is a list of lists where each list contains 
    tuples of plagiarised codes with first item as the name of the student
    and second item as the percentage of similarity with the reference 
    code, while first item in this list will be the reference code.
    """
    codes = _format_codes(codes)

    grouped_cheaters = []
    for _ in range(len(codes)):
        plag = detect(codes)
        ref_code_name = next(iter(codes))
        temp_list = []

        for code in plag:
            plag_percent = round(code[1][0].plagiarism_percent*100, 2)
            if plag_percent >= threshold_percent:
                temp_list.append([
                    code[0], 
                    _get_original_code(codes[code[0]]), 
                    plag_percent
                    ])
                del codes[code[0]]

        if temp_list:
            temp_list.insert(0,[ref_code_name,
                                _get_original_code(codes[ref_code_name])]
                            )
            grouped_cheaters.append(temp_list)
            del codes[ref_code_name]
        
        if not codes:
            break
    return grouped_cheaters
