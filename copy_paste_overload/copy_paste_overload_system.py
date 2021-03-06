from maya import cmds
from maya import mel


class LocalConstants:
    option_var_key = "ClipboardOverloadMapping"


lk = LocalConstants

function_mappings = {
    "clipboard_transforms": {
        "nice_name": "TransformClipboard Copy Paste",
        "copy": "import copy_paste_overload.clipboard_transforms; copy_paste_overload.clipboard_transforms.copy_selected_transforms_to_clipboard()",
        "paste": "import copy_paste_overload.clipboard_transforms; copy_paste_overload.clipboard_transforms.paste_transforms_from_clipboard()",
    },
    "clipboard_skinning": {
        "nice_name": "Skinning/Transform Clipboard (for TechAnims)",
        "copy": "import copy_paste_overload.clipboard_skinning; copy_paste_overload.clipboard_skinning.copy_vertex_weight_or_transforms()",
        "paste": "import copy_paste_overload.clipboard_skinning; copy_paste_overload.clipboard_skinning.paste_vertex_weight_or_transforms()",
    },
}


def overload_copy_paste(target_mapping, allow_ui=True, *args, **kwargs):
    """
    Yes, this looks a bit wonky at first glance.

    But by only overloading this specific mel proc we get all the other niceties in graph editor and so on.

    """
    print("Setting up copy-paste-overload: {}".format(target_mapping))

    # hit reset first to source all the mel commands
    reset_copy_paste()

    target_mapping_info = function_mappings.get(target_mapping)
    if not target_mapping_info:
        cmds.warning(
            "Mapping not found: '{}', copy-paste will not be overriden. Available mappings: '{}'".format(target_mapping,
                                                                                                         ", ".join(
                                                                                                             function_mappings.keys())))
        return

    run_command_copy = target_mapping_info.get("copy")
    run_command_paste = target_mapping_info.get("paste")

    mel.eval('''global proc cutCopyScene(int $cut){{
    python("{}");
    }}'''.format(run_command_copy))

    mel.eval('''global proc pasteScene(){{
    python("{}");
    }}'''.format(run_command_paste))

    cmds.optionVar(stringValue=(lk.option_var_key, target_mapping))

    if allow_ui:
        ensure_default_copy_paste_is_connected()

    return True


def ensure_default_copy_paste_is_connected():
    default_hotkey_mapping = {
        "Ctrl+C": "CopySelectedNameCommand",
        "Ctrl+V": "PasteSelectedNameCommand",
    }

    missing_shortcuts = []
    for shortcut, shortcut_command in default_hotkey_mapping.items():
        if cmds.hotkey(shortcut, q=True, name=True) != shortcut_command:
            missing_shortcuts.append(shortcut)

    if missing_shortcuts:
        confirm = cmds.confirmDialog(
            title='Copy Paste Overload',
            message="CopyPasteOverload requires the default copy paste shortcuts to be connected.\nRe-connect shortcuts to default: '{}'".format(
                ", ".join(missing_shortcuts)),
            button=["Re-connect", "Cancel"],
            defaultButton="Re-connect",
            cancelButton="Cancel",
            dismissString="Cancel",
            icon="warning",
        )
        if confirm == "Cancel":
            return

    for shortcut in missing_shortcuts:
        shortcut_command = default_hotkey_mapping.get(shortcut)
        print("Re-connecting {} to default {}".format(shortcut, shortcut_command))
        cmds.hotkey(
            keyShortcut=shortcut.split("+")[-1].lower(),
            ctl="ctrl" in shortcut.lower(),
            name=shortcut_command,
        )


def reset_copy_paste():
    mel.eval("source cutCopyPaste.mel")


def disable_copy_paste_overload():
    print("Disabling copy-paste-overload")
    cmds.optionVar(stringValue=(lk.option_var_key, ""))
    reset_copy_paste()


def setup_world_space_paste_hotkey(*args, **kwargs):
    from . import clipboard_transforms
    func = clipboard_transforms.paste_transforms_from_clipboard

    command = "import {0}; {0}.{1}(world_space=True)".format(func.__module__, func.__name__)

    setup_maya_hotkey("PasteClipboardWorldSpace", "Ctrl+Shift+V", command)


def setup_maya_hotkey(shortcut_name, shortcut, command_str):
    hotkey_set_name = "UserHotkeys"

    # make sure we have a user editable hotkey set active

    # for some reason this doesn't work in batch mode? guessing some prefs aren't initialzed
    if not cmds.about(batch=True):
        if cmds.hotkeySet(current=True, q=True) == "Maya_Default":
            if not cmds.hotkeySet(hotkey_set_name, exists=True):
                cmds.hotkeySet(hotkey_set_name, source="Maya_Default")
            cmds.hotkeySet(hotkey_set_name, edit=True, current=True)

    name_command = '{0}Command'.format(shortcut_name)
    shortcut_key = shortcut.split("+")[-1]

    if not cmds.runTimeCommand(shortcut_name, exists=True):
        cmds.runTimeCommand(
            shortcut_name,
            command=command_str,
            annotation="Paste transform from clipboard into world space",
            category="Custom",
        )

    cmds.nameCommand(
        name_command,
        command=shortcut_name,
        annotation="Paste transform from clipboard into world space",
    )

    cmds.hotkey(keyShortcut=shortcut_key, name=name_command,
                ctl="ctrl" in shortcut.lower(),
                alt="alt" in shortcut.lower(),
                sht="shift" in shortcut.lower()
                )
