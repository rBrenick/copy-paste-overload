import pymel.core as pm
from maya import cmds
from . import clipboard_transforms

SKINNING_COMPONENT_CLASSES = (pm.general.MeshVertex, pm.general.MeshFace, pm.general.MeshEdge)


def is_skinning():
    ctx = pm.currentCtx()
    if pm.contextInfo(ctx, q=True, c=True) == "artAttrSkin":
        return True
    return False


def component_is_selected():
    sel = pm.selected()[0]
    return sel.__class__ in SKINNING_COMPONENT_CLASSES


class MaintainSelection(object):
    """
    Maintains selection and re-activates proper component type mode
    """

    def __init__(self):
        self.arg_types = ["polymeshFace", "polymeshEdge", "polymeshVertex"]
        self.active_type = None
        self.org_sel = None

    def __enter__(self):
        self.org_sel = cmds.ls(sl=True)

        for arg_type in self.arg_types:
            kwargs = {arg_type: True}
            if pm.selectType(q=True, objectComponent=True, **kwargs):
                self.active_type = arg_type
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        type_select_kwargs = {self.active_type: True}
        pm.selectType(objectComponent=True, **type_select_kwargs)
        pm.select(self.org_sel)


def copy_vertex_weight_or_transforms():
    if component_is_selected():

        with MaintainSelection():
            pm.mel.ConvertSelectionToVertices()
            cmds.select(cmds.ls(sl=True, flatten=True)[0])

            pm.mel.artAttrSkinWeightCopy()

    else:
        clipboard_transforms.copy_selected_transforms_to_clipboard()


def paste_vertex_weight_or_transforms():
    if component_is_selected():
        pm.mel.artAttrSkinWeightPaste()
    else:
        clipboard_transforms.paste_transforms_from_clipboard()
