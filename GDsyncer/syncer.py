from Drive import GoogleDrive, Watcher, bcolors
import sys
from termcolor import cprint
import argparse


def main():
    parser = argparse.ArgumentParser(description="Sync folder with Google Drive")
    parser.add_argument('--name', '-n', type=str, required=True, dest='name', help="Exact name of the GDrive folder")
    parser.add_argument('--dir', '-d', type=str, required=True, dest='path', help="Path to the local folder")
    args = parser.parse_args()
    my_drive = GoogleDrive('../data/client_id.json')
    my_drive.authenticate()
    watcher = Watcher(args.name, args.path, my_drive)
    print("\033[95m Syncing files \033[0m")
    watcher.pull()
    watcher.push()


if __name__ == "__main__":
    main()
