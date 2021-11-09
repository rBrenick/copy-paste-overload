from . import copy_paste_overload_system as cpos
from .ui import ui_utils


class CopyPasteOverloadWindow(ui_utils.BaseWindow):
    def __init__(self):
        super(CopyPasteOverloadWindow, self).__init__()

        self.setWindowTitle("Copy Paste Overload")

        for cb_key, cb_data in cpos.function_mappings.items():
            self.add_button(cb_data.get("nice_name"), cpos.overload_copy_paste, cb_key)
        self.add_button("Setup 'Ctrl+Shift+V' World Space Paste", cpos.setup_world_space_paste_hotkey)
        self.add_button("Reset Copy Paste", cpos.disable_copy_paste_overload)


def main():
    win = CopyPasteOverloadWindow()
    return win
