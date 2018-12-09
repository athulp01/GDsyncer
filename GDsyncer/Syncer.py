from Drive import GoogleDrive, Watcher, bcolors
import sys
from termcolor import cprint


def main():
    if len(sys.argv) < 3:
        cprint("Please provide the name of the GDrive folder and path to the local folder as arguments",
               'red', attrs=['bold'], file=sys.stderr)
        sys.exit(1)

    path = sys.argv[2]
    name = sys.argv[1]
    my_drive = GoogleDrive('config.dat')
    my_drive.authenticate('credentials.dat')
    watcher = Watcher(name, path, my_drive)
    print("\033[95m Syncing files \033[0m")
    watcher.pull()
    watcher.push()


if __name__ == "__main__":
    main()
