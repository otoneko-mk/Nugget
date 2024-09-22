from .tweak_classes import Tweak, TweakModifyType
from Sparserestore.restore import FileToRestore
from devicemanagement.constants import Version

import plistlib
import sys
from pathlib import Path
from os import path, getcwd

class InvalidRegionCodeException(Exception):
    "Region code must be exactly 2 characters long!"
    pass

def replace_region_code(plist_path: str, original_code: str = "US", new_code: str = "US"):
    with open(plist_path, 'rb') as f:
        plist_data = plistlib.load(f)
    
    plist_str = str(plist_data)
    updated_plist_str = plist_str.replace(original_code, new_code)
    updated_plist_data = eval(updated_plist_str)  # Convert string back to dictionary

    return plistlib.dumps(updated_plist_data)

class EligibilityTweak(Tweak):
    def __init__(
            self, label: str,
            min_version: Version = Version("1.0"),
            divider_below: bool = False
        ):
        super().__init__(label=label, key=None, value=["Method 1", "Method 2"], edit_type=TweakModifyType.PICKER, min_version=min_version, divider_below=divider_below)
        self.code = "US"
        self.method = 0 # between 0 and 1

    def set_region_code(self, new_code: str):
        if new_code == '':
            self.code = "US"
        else:
            self.code = new_code

    def set_selected_option(self, new_method: int):
        self.method = new_method % 2 # force it to be either 0 or 1
        self.set_enabled(True)

    def get_selected_option(self) -> int:
        return self.method

    def apply_tweak(self) -> list[FileToRestore]:
        # credit to lrdsnow for EU Enabler
        # https://github.com/Lrdsnow/EUEnabler/blob/main/app.py
        if not self.enabled:
            return None
        print(f"Applying EU Enabler for region \'{self.code}\'...")
        # get the plists directory
        try:
            source_dir = path.join(sys._MEIPASS, "files/eligibility")
        except:
            source_dir = path.join(getcwd(), "files/eligibility")

        # start with eligibility.plist
        file_path = path.join(source_dir, 'eligibility.plist')
        eligibility_data = replace_region_code(file_path, original_code="US", new_code=self.code)
        files_to_restore = [
            FileToRestore(
                contents=eligibility_data,
                restore_path="/var/db/os_eligibility/",
                restore_name="eligibility.plist"
            )
        ]

        # next modify config.plist
        file_path = path.join(source_dir, 'Config.plist')
        config_data = replace_region_code(file_path, original_code="US", new_code=self.code)
        if self.method == 0:
            files_to_restore.append(
                FileToRestore(
                    contents=config_data,
                    restore_path="/var/MobileAsset/AssetsV2/com_apple_MobileAsset_OSEligibility/purpose_auto/c55a421c053e10233e5bfc15c42fa6230e5639a9.asset/AssetData/",
                    restore_name="Config.plist"
                )
            )
        elif self.method == 1:
            files_to_restore.append(
                FileToRestore(
                    contents=config_data,
                    restore_path="/var/MobileAsset/AssetsV2/com_apple_MobileAsset_OSEligibility/purpose_auto/247556c634fc4cc4fd742f1b33af9abf194a986e.asset/AssetData/",
                    restore_name="Config.plist"
                )
            )
        
        # return the new files to restore
        return files_to_restore
    