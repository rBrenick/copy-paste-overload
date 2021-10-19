import json
import sys

import pymel.core as pm
from PySide2 import QtWidgets


def get_depth_sorted_nodes():
    """
    sort selected nodes by depth, so when applying in world space, setting the transforms requires less iterations
    """
    return sorted(pm.selected(type="transform"), key=lambda x: len(x.longName().split("|")))


def copy_selected_transforms_to_clipboard():
    all_node_data = {}

    depth_sorted_nodes = get_depth_sorted_nodes()

    for node in depth_sorted_nodes:
        node_data = {}
        attribute_data = {}
        for visible_attr in pm.listAttr(node, keyable=True):
            attribute_data[visible_attr] = node.getAttr(visible_attr)

        node_data["attributes"] = attribute_data
        node_data["world_matrix"] = [item for sublist in node.getMatrix(worldSpace=True) for item in sublist]

        all_node_data[node.nodeName()] = node_data

    app = QtWidgets.QApplication.instance()
    cb = app.clipboard()
    cb.setText(json.dumps(all_node_data, indent=2))
    sys.stdout.write("Copied {} transform(s) to clipboard\n".format(len(all_node_data.keys())))


def paste_transforms_from_clipboard(world_space=False):
    app = QtWidgets.QApplication.instance()
    cb = app.clipboard()
    all_node_data = json.loads(cb.text())

    iteration_count = 5 if world_space else 1

    existing_nodes = []
    sel = pm.selected()
    for node_name, node_data in all_node_data.items():
        if not pm.objExists(node_name):
            continue

        node = pm.PyNode(node_name)

        # if controls selected, only paste on them
        if sel and node not in sel:
            continue

        existing_nodes.append(node)

    # only one thing selected, remap transform to selected
    if not any(existing_nodes) and sel:
        first_selected = sel[0]
        sys.stdout.write("No matching transforms found, remapping to '{}'\n".format(first_selected.name()))
        existing_nodes = [first_selected]
        all_node_data[first_selected.name()] = all_node_data.values()[0]

    world_space_affecting_attrs = ["translateX", "translateY", "translateZ",
                                   "rotateX", "rotateY", "rotateZ",
                                   "scaleX", "scaleY", "scaleZ",
                                   "space"]

    # set transform a couple times when in world space
    # this is because dependencies might be set out of order
    for i in range(iteration_count):
        for node in existing_nodes:
            node_data = all_node_data.get(node.name())

            for attribute_name, attribute_value in node_data.get("attributes", {}).items():
                # skip transform and space attributes when pasting to world space
                if world_space and attribute_name in world_space_affecting_attrs:
                    continue

                # skip if attribute doesn't exist
                if not pm.attributeQuery(attribute_name, exists=True, node=node):
                    continue

                # skip if attribute is locked or something like that
                if not node.getAttr(attribute_name, settable=True):
                    continue

                node.setAttr(attribute_name, attribute_value)

            if world_space:
                node.setMatrix(node_data.get("world_matrix"), worldSpace=True)

    sys.stdout.write("Pasted {} transform(s) from clipboard\n".format(len(existing_nodes)))
