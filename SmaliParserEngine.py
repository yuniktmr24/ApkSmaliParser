import re
import os
import argparse
import SmaliParser
import datetime
import pandas as pd
from pystreamapi import Stream
def main():
    ROOT_DECOMPILATION_DIRECTORY = "./decompiled"
    # smaliParser = initializeSmaliParser(os.path.join(ROOT_DECOMPILATION_DIRECTORY))
    # smaliParser.analyze_smali_file("/Users/yuniktamrakar/Documents/MedAn/mobile/scripts/decompiled/Instagram/smali_classes5/X/Dty.3.smali")
     #path to the apk file for decompilation using APKTool
    parser = argparse.ArgumentParser(description='Path to the apk file for decompilation into .smali')
    parser.add_argument("-v", "--verbose", action="store_true", help="Control output verbosity")
    group = parser.add_mutually_exclusive_group()
    # group.add_argument("-v", "--verbose", action="store_true", type=int, choices=[0, 1],
    #                     help="Control output verbosity")
    # group.add_argument("-q", "--quiet", action="store_true")

    group.add_argument('-p', '--path', help='Path to a single apk file for decompilation into .smali')
    group.add_argument('-d', '--dir', help='Path to a directory containing apk files for decompilation into .smali')

    args = parser.parse_args()   
    verbose = False
    if args.verbose:
        verbose = True
    use_apktool(args)
    answer = ask_user_yes_no("Proceed with smali analyis?")
    runtime = {}
    # If the user entered yes, continue the program.
    if answer == "yes":
        subdirectories = os.listdir(ROOT_DECOMPILATION_DIRECTORY)
        #print(subdirectories)
        #initializeSmaliParser("./decompiled/app-debug-androidTest")
        for decompiled_app in subdirectories:
            #analysis phase benchmarking start
            start_time = datetime.datetime.now()
            smaliParser= initializeSmaliParser(os.path.join(ROOT_DECOMPILATION_DIRECTORY, decompiled_app)) #each decompiled app should have its own smaliParser obj
            #print(smaliParser.get_smali_files())
            i = 0
            for file in smaliParser.get_smali_files():
                if (smaliParser.all_privacy_practices_found == True):
                    break
                smaliParser.analyze_smali_file(file)
                #print(smaliParser.get_matching_privacy_practices())
            #print(os.path.join(DECOMPILATION_DIRECTORY, decompiled_app))

            if verbose:
                print(smaliParser.get_matching_privacy_practices())
                print("***** Files with first match for privacy practices :", smaliParser.get_first_file_with_match(), "*************")
            smaliParser.write_to_xls(decompiled_app)
              #analysis phase benchmarking end
            end_time = datetime.datetime.now()
            execution_time = end_time - start_time
            print('********************************')
            print("Analysis phase Execution time for {} app: {} ".format(decompiled_app, execution_time))
            print('********************************')
            runtime[decompiled_app] = execution_time
    else:
        exit()
    benchmark(runtime, True, subdirectories)
  
def benchmark(runtimeInfo, export = False, subdirectories = None):
    total_seconds = 0
    for value in runtimeInfo.values():
        total_seconds += value.total_seconds()
    print("Time ", runtimeInfo)
    print('********************************')
    print("Total Analysis time = ", total_seconds)
    print('********************************')
    if export == True and subdirectories != None:
        df = pd.DataFrame({"App": subdirectories, "Analysis Time (in seconds)": Stream.of(runtimeInfo.values()).map(lambda val: val.total_seconds()).to_list()})
        df.to_excel('./reports/{}.xlsx'.format("Benchmark"), sheet_name="Analysis-Benchmark", index=False)
    return total_seconds
 
def use_apktool(args):
    #decompile - benchmark start
    start_time = datetime.datetime.now()
    print("********** Decompilation Start *****************")
    if args.path:
        # Decompile the single apk file
        file_name = extract_apk_filename(args.path)
        decompile(file_name, args.path)
    elif args.dir:
        # Decompile all the apk files in the directory
        # Get the list of all files in the directory `apks`
        files = os.listdir(args.dir)
        apk_files = [file for file in files if file.endswith('.apk')]
        # Print the list of files
        print('Files in the directory `apks`:' + str(apk_files))
        idx = 1
        for file in apk_files:
            current_apk_path = ""
            print("***** Decompiling apk {} out of {} ****".format(idx, len(apk_files)))
            if (args.dir.endswith("/")):
                current_apk_path = args.dir + file
            else:
                current_apk_path = args.dir + "/"+ file
            file_name = extract_apk_filename(current_apk_path)
            decompile(file_name, current_apk_path)
            idx += 1
            
    else:
        # Print an error message
        print('Specify either the path to a single apk file or the path to a directory containing apk files if you havent already done so before')

    
    # if (args.verbose) > 0:
    # print("Decompilation started")
    print("********** Decompilation End *****************")
    #decompile phase benchmarking end
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    print('********************************')
    print("Decompilation phase Execution time:", execution_time)
    print('********************************')
  
def extract_apk_filename(filepath):
    return re.search(r"([^/]*)\.apk$", filepath).group(1)

def decompile(decompiled_folder_name, apk_path):
    os.system("apktool d -f -o ./decompiled/{} -f {}".format(decompiled_folder_name, apk_path))

def initializeSmaliParser(path):
    smaliParser = SmaliParser.SmaliParser(path) #initiailize object with the decompiled app outer directory
    smaliParser.print_smali_file_info(False) 
    return smaliParser

def ask_user_yes_no(question):
    while True:
        answer = input(question + " (yes/no): ")
        answer = answer.lower().strip()
        if answer in ("yes", "no"):
            return answer
        else:
            print("Invalid response. Please enter yes or no.")

if __name__ == "__main__":
	main()