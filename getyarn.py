import downloader
from zipfile import ZipFile
import os

def getYarnMappings(version:str):
    DOWNLOAD_LINK = f"https://github.com/FabricMC/yarn/archive/{version}.zip"
    ZIP_PATH = f"stich_yarn_tmp_{version}.zip"

    if os.path.exists(f"yarn-{version}"):
        print("Found existing mappings, will use those")
    else:
        print("Could not find existing mappings, this might take a minute")
        print(f"Getting {DOWNLOAD_LINK}")
        downloader.download_url(DOWNLOAD_LINK, ZIP_PATH)

        print("Extracting mappings from zip (Could take upwards of 2 minutes)")
        archive = ZipFile(ZIP_PATH, 'r')
        for zippedFile in archive.namelist():
            if zippedFile.startswith(f"yarn-{version}/mappings/"):
                archive.extract(zippedFile)
        archive.close()
        
        print("Cleaning up zip")
        os.remove(ZIP_PATH)