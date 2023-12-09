# ApkSmaliParser
Python script to decompile APKs into smali files and then parse through the smali files to check for various API calls (privacy practice related APIs for now)

## Running the Script
* First make sure you have the apks you want to decompile in a single directory
* Then Run `python SmaliParserEngine.py -d [path to the apk directory]`
  * The script also supports single apk decompilation using the `-p` argument to specify the apk path
* This should start the script's decompilation phase
* Once, the decompilation is done, then the script will prompt if analysis should begin
* After analysis, the reports of the scripts should be found in the `./reports` directory
