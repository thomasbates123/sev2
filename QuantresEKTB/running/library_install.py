import subprocess
import sys



def install_libraries(libraries):
    try:
        for library in libraries:
            subprocess.run([sys.executable, '-m', 'pip', 'install', library], check=True)
            print(f"{library} has been installed.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing {library}: {e}")

if __name__ == "__main__":
    # List of libraries to install
    libraries_to_install = [
        'requests',
        'numpy',
        'pandas',
        'matplotlib',
        'xbbg',
        'datetime',
        'pathlib',
        'statsmodels'
        'blpapi',
        'alpaca-trade-api'
    ]

    # Install the libraries
    install_libraries(libraries_to_install)

    # Install blpapi from the specified index URL
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/", "blpapi"])