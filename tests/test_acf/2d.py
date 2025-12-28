#!/usr/bin/env python
# -*-coding: utf-8-*-
from kmos.types import Action, Condition, Project, Site
import numpy as np

pt = Project()
pt.set_meta(
    author="Andreas Garhammer",
    email="andreas-garhammer@t-online.de",
    model_name="2d_auto",
    model_dimension=2,
)


pt.add_species(name="empty", representation="Atoms('He')")


pt.add_species(name="ion", representation="Atoms('F')")


# Definition of grid with the name: 2d_grid
layer = pt.add_layer(name="default")


layer.sites.append(Site(name="a_1", pos="0.25 0.25 0.5", default_species="ion"))

layer.sites.append(Site(name="a_2", pos="0.75 0.25 0.5", default_species="ion"))

layer.sites.append(Site(name="b_1", pos="0.25 0.75 0.5 ", default_species="empty"))

layer.sites.append(Site(name="b_2", pos="0.75 0.75 0.5", default_species="empty"))


pt.lattice.cell = np.array([3.5, 3.5, 10])

# Parameters
pt.add_parameter(name="k", value=100, adjustable=True, min=0, max=10e5)


# Coordinates
a_1 = pt.lattice.generate_coord("a_1.(0,0,0).default")
a_2 = pt.lattice.generate_coord(
    "a_2.(0,0,0).default"
)  # a_2.(0,0,0).lto: tetra.l.2 in der Zelle 000 von lto
b_1 = pt.lattice.generate_coord("b_1.(0,0,0).default")
b_2 = pt.lattice.generate_coord("b_2.(0,0,0).default")


# Processes

# Processes from a_1
pt.add_process(
    name="a_1_a_2",
    conditions=[
        Condition(species="ion", coord=a_1),
        Condition(species="empty", coord=a_2),
    ],
    actions=[Action(species="ion", coord=a_2), Action(species="empty", coord=a_1)],
    rate_constant="k",
)

pt.add_process(
    name="a_1_b_1",
    conditions=[
        Condition(species="ion", coord=a_1),
        Condition(species="empty", coord=b_1),
    ],
    actions=[Action(species="ion", coord=b_1), Action(species="empty", coord=a_1)],
    rate_constant="k",
)

pt.add_process(
    name="a_1_b_2",
    conditions=[
        Condition(species="ion", coord=a_1),
        Condition(species="empty", coord=b_2),
    ],
    actions=[Action(species="ion", coord=b_2), Action(species="empty", coord=a_1)],
    rate_constant="k",
)


# Processes from a_2
pt.add_process(
    name="a_2_a_1",
    conditions=[
        Condition(species="ion", coord=a_2),
        Condition(species="empty", coord=a_1),
    ],
    actions=[Action(species="ion", coord=a_1), Action(species="empty", coord=a_2)],
    rate_constant="k",
)

pt.add_process(
    name="a_2_b_1",
    conditions=[
        Condition(species="ion", coord=a_2),
        Condition(species="empty", coord=b_1),
    ],
    actions=[Action(species="ion", coord=b_1), Action(species="empty", coord=a_2)],
    rate_constant="k",
)

pt.add_process(
    name="a_2_b_2",
    conditions=[
        Condition(species="ion", coord=a_2),
        Condition(species="empty", coord=b_2),
    ],
    actions=[Action(species="ion", coord=b_2), Action(species="empty", coord=a_2)],
    rate_constant="k",
)

# Processes from b_1
pt.add_process(
    name="b_1_a_1",
    conditions=[
        Condition(species="ion", coord=b_1),
        Condition(species="empty", coord=a_1),
    ],
    actions=[Action(species="ion", coord=a_1), Action(species="empty", coord=b_1)],
    rate_constant="k",
)

pt.add_process(
    name="b_1_a_2",
    conditions=[
        Condition(species="ion", coord=b_1),
        Condition(species="empty", coord=a_2),
    ],
    actions=[Action(species="ion", coord=a_2), Action(species="empty", coord=b_1)],
    rate_constant="k",
)

pt.add_process(
    name="b_1_b_2",
    conditions=[
        Condition(species="ion", coord=b_1),
        Condition(species="empty", coord=b_2),
    ],
    actions=[Action(species="ion", coord=b_2), Action(species="empty", coord=b_1)],
    rate_constant="k",
)


# Processes from b_2
pt.add_process(
    name="b_2_a_1",
    conditions=[
        Condition(species="ion", coord=b_2),
        Condition(species="empty", coord=a_1),
    ],
    actions=[Action(species="ion", coord=a_1), Action(species="empty", coord=b_2)],
    rate_constant="k",
)

pt.add_process(
    name="b_2_a_2",
    conditions=[
        Condition(species="ion", coord=b_2),
        Condition(species="empty", coord=a_2),
    ],
    actions=[Action(species="ion", coord=a_2), Action(species="empty", coord=b_2)],
    rate_constant="k",
)

pt.add_process(
    name="b_2_b_1",
    conditions=[
        Condition(species="ion", coord=b_2),
        Condition(species="empty", coord=b_1),
    ],
    actions=[Action(species="ion", coord=b_1), Action(species="empty", coord=b_2)],
    rate_constant="k",
)


# Export
pt.filename = "2d_grid.xml"
pt.save()
