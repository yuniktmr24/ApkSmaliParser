import os
from collections import Counter
import glossary
import re
import itertools
import pandas as pd

class SmaliParser():
    # Find all of the `.smali` files in the current directory and its subdirectories.
    def __init__(self, path):
        self.smali_path = path #outer folder for the decompiled-app
        self.smali_files = []
        self.smali_files_count = 0
        self.api_map = {}
        self.matching_privacy_practices = []
        self.all_privacy_practices_found = False
        self.first_file_with_match = {}

    #walk into the smali files contained within the sub-directories
    def _find_smali_files(self):
        directory = self.smali_path
        for root, directories, files in os.walk(directory):
            for file in files:
                if file.endswith('.smali'):
                    self.smali_files_count += 1
                    smali_path = os.path.join(root, file)
                    self.smali_files.append(smali_path)
                    #yield smali_path
    

    # Print the names of all of the `.smali` files.
    def print_smali_file_info(self, verbose=False):
        if (self.smali_files == []):
            self._find_smali_files()
        if verbose == True:
            for smali_file in self.smali_files:
                print(smali_file)
        print("----------------")
        print(self.smali_files_count , "smali files were found under the directory "+self.smali_path)
        print("----------------")
    
    def get_smali_files(self):
        return self.smali_files
    
    def get_matching_privacy_practices(self): #privacy practices found in smali code
        return self.matching_privacy_practices

    def analyze_smali_file(self, file_name, comprehensive=False):
        standardized_api_names = []
        api = self._extract_api_calls(file_name)
        for name in api:
            _, _, lib, method = name
            api_raw = lib + ("." + method if method is not None else "")
            std = (self._standardize_api_names(api_raw))
            standardized_api_names.append(std)
            
        #print(standardized_api_names)
        privacy_practices_glossary = list(itertools.chain.from_iterable(glossary.GLOSSARY.values()))
        
        if (self.all_privacy_practices_found == False):
            for sensitive_api in privacy_practices_glossary:
                if (sensitive_api not in self.matching_privacy_practices):
                    if (any(sensitive_api in t for t in standardized_api_names)):
                        self.matching_privacy_practices.append(sensitive_api)
                        self.first_file_with_match[sensitive_api] = file_name
                        if (len(self.matching_privacy_practices) == len(privacy_practices_glossary)):
                            self.all_privacy_practices_found = True

        if comprehensive:
            #count number of occurences
            counter = Counter()
            for standardized_api_name in standardized_api_names:
                for glossary_term in privacy_practices_glossary:
                    if glossary_term in standardized_api_name:
                        counter[glossary_term] += 1
            print(counter.items())

            self.api_map[file_name] = counter.items()
            print(self.api_map)
                
            print(len(api))

    def _extract_api_calls(self, smali_file):
        api_calls = []

        with open(smali_file, "r") as f:
            for line in f:
                match = re.search(r"(invoke-.*).*\{(.*)\},(.+);+(->)*(.+)*", line)
                if match:
                    method_type = match.group(1)
                    arguments = match.group(2).split(",")
                    api = match.group(3)
                    method = match.group(5)
                    api_calls.append((method_type, arguments, api, method))

        return api_calls

    def _standardize_api_names(self, smali_format_apis):
        return smali_format_apis.replace("/", ".").replace(";->", ".")
    
    def get_first_file_with_match(self):
        return self.first_file_with_match
    
    def write_to_xls(self, outputName):
        if (self.first_file_with_match != {}):
            found_privacy_apis = list(self.first_file_with_match.keys())
            found_privacy_practices = []

            api_to_category_map = {method_name: key for key, values in glossary.GLOSSARY.items() for method_name in values}
            
            for api in found_privacy_apis:
                corresponding_key = api_to_category_map.get(api, None)
                found_privacy_practices.append(corresponding_key)

            first_files = self.first_file_with_match.values()
            df = pd.DataFrame({'Matched Privacy Categories': found_privacy_practices, 'Matched Privacy related APIs': found_privacy_apis, 'First File with Match': first_files})
            print(df)
            df.to_excel('./reports/{}.xlsx'.format(outputName), sheet_name="sheet1", index=False)

    