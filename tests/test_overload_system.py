from maya import cmds

from base import MayaBaseTestCase

import copy_paste_overload.copy_paste_overload_system as cpos


class TestOverloadSystem(MayaBaseTestCase):
    
    def test_setup_transform_clipboard(self):
        """Test whether system can overload the maya clipboard"""
        return_val = cpos.overload_copy_paste("clipboard_transforms")
        self.assertTrue(return_val)
        
        option_var_value = cmds.optionVar(query=cpos.lk.option_var_key)
        self.assertEqual(option_var_value, "clipboard_transforms")

    def test_reset_clipboard(self):
        """Test whether system can reset to the default maya clipboard"""
        
        # first overload
        cpos.overload_copy_paste("clipboard_transforms")
        
        # then run the reset
        cpos.disable_copy_paste_overload()
        
        # option_var should be an empty string when it's reset
        mapping_var = cmds.optionVar(query=cpos.lk.option_var_key)
        self.assertEqual(mapping_var, "")
        
    def test_setup_world_space_hotkey(self):
        """Test whether normal style hotkey can be created"""
        
        command_name = "PasteClipboardWorldSpace"
        
        # setup hotkey
        cpos.setup_maya_hotkey(command_name, "Ctrl+Shift+V", "print('empty_command')")
        
        command_exists = cmds.runTimeCommand(command_name, exists=True)
        self.assertTrue(command_exists)
