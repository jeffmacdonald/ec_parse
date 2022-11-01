from collections import OrderedDict
import argparse
from argparse import ArgumentParser
import os.path
import sys
import re


# https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do
# https://realpython.com/introduction-to-python-generators/
def slices(s, args):
    position = 0
    for length in args:
        length = int(length)
        line = s[position:position + length]
        position += length

        # MAGIC
        # This is where you can easily apply
        # filters to "res" just follow this pattern, where;
        # "something" can be any test you want
        # "whatever" can be any variety of conditions
        # if something:
        #      yield "whatever"
        #      continue
        if "9999.9" in line:
            yield "na"
            continue
        if line.startswith('a'):
            # these are called Regular expressions. ^ means start of files \s* means "a bunch of spaces"
            line = re.sub(r"^a\s*", "", line)
            yield line.strip()
            continue

        # yield the raw value, with leading and trailing spaces stripped off the end
        yield line.strip()


def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x


def parse_files(args, InputFile, fieldNames, fieldLength):
    OutputFile = str(InputFile) + ".csv"
    DELIMITER = args.Delimiter

    # This is where we actually process the files
    # And where we'd do things like either skip the first few lines, or process them differently or whatever.
    with open(OutputFile, 'w') as f1:
        fieldNames = DELIMITER.join(map(str, fieldNames))
        f1.write(fieldNames + "\n")
        linenumber = 0
        with open(InputFile, 'r') as f:
            for line in f:
                linenumber += 1

                # MAGIC
                # skip the first few lines, or optionally treat them differently
                if linenumber == 1:
                    line_sections = line.split(",")
                    rec = "FILE ID is :  " + line_sections[0]
                    myLine = rec
                elif linenumber == 2:
                    continue
                elif linenumber == 3:
                    continue
                elif linenumber == 4:
                    continue
                else:
                    rec = (list(slices(line, fieldLength)))
                    myLine = DELIMITER.join(map(str, rec))

                f1.write(myLine + "\n")


def parse_dir(args, dir):
    fieldNames = []
    fieldLength = []
    myvars = OrderedDict()

    # Read the config file
    with open(ConfigFile) as myfile:
        for line in myfile:
            name, var = line.partition(",")[::2]
            myvars[name.strip()] = int(var)
    for key, value in myvars.items():
        fieldNames.append(key)
        fieldLength.append(value)

    for dirname, dirnames, filenames in os.walk(dir + '/'):
        for filename in filenames:
            parse_files(args, dirname + filename, fieldNames, fieldLength)


parser = ArgumentParser(
    description="Please provide your Inputs as -c ConfigFile -d Delimiter")
parser.add_argument("-c", dest="ConfigFile", required=False,
                    help="Provide your Config file name here,File should have value as fieldName,fieldLength. if file is on different path than where this script resides then provide full path of the file", metavar="FILE", type=extant_file)
parser.add_argument("-d", dest="Delimiter", required=False,
                    help="Provide the delimiter string you want", metavar="STRING", default="|")
args = parser.parse_args()

# Config file check
if args.ConfigFile is None:
    if not os.path.exists("Config.txt"):
        print("There is no Config File provided exiting the script")
        sys.exit()
    else:
        ConfigFile = "Config.txt"
        print("Taking Config.txt file on this path as Default Config File")
else:
    ConfigFile = args.ConfigFile

parse_dir(args, 'min')
parse_dir(args, 'max')
