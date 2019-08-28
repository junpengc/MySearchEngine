# Main module of Program MySearch Engine
# Author: Junpeng Chen 26747553
#


import sys;
import os;
import Index;
import Search;


# Validate command line input
def validate(args):
    available_commands = ['index','search','help'];
    if len(args) <= 4:
        print_help();
        return False;

    if args[1].lower() not in available_commands:
        print("**Error: Command not found.**");
        print("**Available_command:", available_commands);
        return False;
    elif args[1].lower() == 'index':
        if not os.path.isdir(args[2]):
            print("**Error: Collection directory not found.**");
            return False;
        if not os.path.isfile(args[4]):
            print("**Error: StopWord file not found.**");
            return False;

    elif args[1].lower() == 'search':
        if not os.path.isdir(args[2]):
            print("**Error: Index directory not found.**");
            return False;
        else:
            index_file_path = os.path.join(args[2],'index.txt');
            if not os.path.isfile(index_file_path):
                print(index_file_path);
                print("**Error: Index file not found.**");
                return False;

        if not args[3].isdigit():
            print("**Error: Input Correct document number.**")
            return False;
        if len(args[3:]) == 0:
            print("**Error: You need at least give one keyword.");
            return False;

    return True;


def print_help():
    print("To use this program, you need to provide parameters as in follow format:\n");
    print("1.Index: ");
    print("  MySearchEngine index [collection_dir] [a dir to store index file] [stopword file] \n");
    print("2.Search: ");
    print("  MySearchEngine search [index_dir] [num_docs] [[a list of keywords]] \n");
    print("3.help: ");
    print("  MySearchEngine help \n");
    print("Have for using the next generation of google!");



def print_a_line_of_star():
    print("***********************************************************************************");

if __name__ == "__main__":
    print_a_line_of_star();
    if not validate(sys.argv):
        print_a_line_of_star();
        exit();
    if sys.argv[1].lower() == 'index':
        Index.index_collection(*sys.argv[2:]);
    elif sys.argv[1].lower() == 'search':
        Search.search(sys.argv[2],sys.argv[3],sys.argv[4:])
    else:
        print_help();

    print_a_line_of_star();
    input("Press 'Enter' to quit");
    
