def main():
    from . import copy_paste_overload_ui
    return copy_paste_overload_ui.main()


def reload_module():

    import sys
    if sys.version_info.major >= 3:
        from importlib import reload
    else:
        from imp import reload

    from . import clipboard_transforms
    from . import clipboard_skinning
    from . import copy_paste_overload_system
    from . import copy_paste_overload_ui
    reload(clipboard_transforms)
    reload(clipboard_skinning)
    reload(copy_paste_overload_system)
    reload(copy_paste_overload_ui)


def startup():
    from maya import cmds
    user_clipboard_mapping = cmds.optionVar(query="ClipboardOverloadMapping")

    # early exit if user doesn't have any clipboard override defined
    if not user_clipboard_mapping:
        return

    from . import copy_paste_overload_system as cpos
    setup_overload_func = cpos.function_mappings.get(user_clipboard_mapping)

    if setup_overload_func:
        cpos.overload_copy_paste(user_clipboard_mapping, allow_ui=False)
