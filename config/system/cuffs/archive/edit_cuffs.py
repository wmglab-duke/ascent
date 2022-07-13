#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Used to add descriptions to cuff json parameters
"""


import json
import os

# if parameter in value list, it will be renamed to key
# rename_dict = {
#     "L_cuff": ["L"],
#     "Pitch": ["sep_wire", "sep_elec", "pitch", "sep_wire"],
#     "w_elec": ["w_contact"],
#     "Thk_elec": ["thk_contact"],
#     "Center": ["z_center"],
#     "theta_cuff": ["Theta"],
#     "Theta_contact": ["contact_wrap", "theta_contact", "theta_wire"],
#     "L_elec": ["z_contact"],
#     "Recess": ["recess"],
# }

# Add description to parameters with this prefix
descript = {
    'R_in': "Cuff inner diameter",
    'R_out': "Cuff outer diameter",
    'thk_medium_gap_internal': "Gap between cuff and nerve",
    'Thk_fill': "Distance fill extends beyond cuff boundary",
    "L_cuff": "Length of cuff",
    'Thk_elec': "Thickness of contact",
    'Center': "Z-position of cuff center",
    'r_cuff_in_pre': "Cuff resting inner diameter",
    'L_elec': "Z-length of contact",
    'thk_cuff': 'Cuff thickness',
    'w_elec': "Contact width",
    'Theta_contact': "Angular coverage of contact",
    'Pitch': "z-distance between contacts",
    'theta_cuff': "Angular coverage of cuff",
    'N_holes': "Can have the value of 1 or 2. Adds conical shaped holes in TubeCuff. If 1 hole, centered longitudinally in cuff. If 2, evenly spaced by Pitch_holecenter_holecenter about longitudinal center of cuff",
    'Rot_def': "Rotates TubeCuff CCW by angle",
    'D_hole': "Diameter of holes in TubeCuff at the surface of the inner diameter",
    'Buffer_hole': "Used so that the cone used to cut hole in the cuff extends half this distance from the inner and outer edge of the part",
    'L_holecenter_cuffseam': "Distance from edge of the cuff seam to the center of the holes",
    'Pitch_holecenter_holecenter': "Distance between cuff holes, pitch from center to center along the length of the cuff",
    'Recess': "Depth of fill material into the cuff before the contact. This is used to create an associated recess/fill domain with a contact.",
    'Rot_def_contact': "Rotation/orientation of ribbon contact. CWW. Contact is oriented with CW edge at 0 deg (3 o'clock) and extends CCW.",
    'percent_circ_cuff': "Wrap of the cuff (as compared to 360 degree wrap for continuous insulation) after expansion to accommodate the nerve",
    'B': "Arc length of contact around the cuff",
    'percent_circ_cuff_pre': "Wrap of the cuff (as compared to 360 degree wrap for continuous insulation) before expansion to accommodate the nerve",
    'arc_ext': "Length beyond which the cuff extends from the contact on either edge around the circumference",
    'theta_contact_pre': "Angle of the contact before expansion to accommodate the nerve",
    'Tangent': "MicroLeads contact dimension ... shaped like U in cross section, the Tangent is the length of the straight portions on either side of the curve at the bottom of the U",
    'x_shift': "Translation of the fill domain in the x direction",
    'y_shift': "Translation of the fill domain in the y direction",
    'gap': "If MicroLeads cuff does not close all the way, this is used to widen the opening.",
    'trap_base': "For 100 um MicroLeads, the cuff cross section looks like a Circle+Trapezoid, with connecting edge the diameter of the circle. This is the length trapezoid base that does not connect with the circle.",
    'fillet_contact': "Fillet for RectangleContact corners",
    'theta_pos_contact1': "Rotational position of contact 1 in Pitt.json",
    'theta_pos_contact2': "Rotational position of contact 2 in Pitt.json",
    'theta_pos_contact3': "Rotational position of contact 3 in Pitt.json",
    'theta_pos_contact4': "Rotational position of contact 4 in Pitt.json",
    'Rect_def': "1 to preserve surface area, 2 to preserve shape of contact to the dimensions provided",
    'r_wire': "Half the gauge of WireContact",
    'percent_circ_wire_pre': "Wrap around angle of WireContact (where 1 is 100%, 0.8 is 80%, ...) before nerve expansion.",
    'percent_circ_wire': "Wrap around angle of WireContact (where 1 is 100%, 0.8 is 80%, ...) after nerve expansion.",
    "L": "Length of cuff",
    "sep_wire": "z-distance between contacts",
    "sep_elec": "z-distance between contacts",
    "pitch": "z-distance between contacts",
    "w_contact": "Contact width",
    "thk_contact": "Thickness of contact",
    "z_center": "Z-position of cuff center",
    "Theta": "Angular coverage of cuff",
    "contact_wrap": "Angular coverage of contact",
    "theta_contact": "Angular coverage of contact",
    "theta_wire": "Angular coverage of contact",
    "z_contact": "Z-length of contact",
    "recess": "Depth of fill material into the cuff before the contact. This is used to create an associated recess/fill domain with a contact.",
}
missing = {}
removed = {}


def renamer(dictre, cuffcon):
    # get params for cuff
    this_param = cuffcon['params']
    for i, param in enumerate(this_param):
        # remove cuff code from param
        namebase = param['name'].replace('_' + cuffcon['code'], '')
        for key, value in dictre.items():
            # go through rename dict and check if this param needs to be renamed
            if namebase in value:
                cuffcon['params'][i]['name'] = key + '_' + cuffcon['code']
    return cuffcon


def descriptor(dictde, cuffcon):
    this_param = cuffcon['params']
    for i, param in enumerate(this_param):
        namebase = param['name'].replace('_' + cuffcon['code'], '')
        stringy = json.dumps(cuffcon)
        instances = stringy.count(param['name'])
        # if instances == 1:
        #     cuffcon['params'].remove(cuffcon['params'][i])
        #     continue
        if namebase == 'z_nerve' or namebase == 'zw_rot':
            cuffcon['params'].remove(cuffcon['params'][i])
            continue
        if namebase in dictde.keys():
            cuffcon['params'][i]['description'] = dictde[namebase]
        else:
            if namebase not in missing.keys():
                missing[namebase] = [file]
            else:
                missing[namebase].append(file)
    return cuffcon


for file in os.listdir():
    if file.endswith('.json') and 'LivaNova' not in file:
        # run on all cuff jsons
        # with open(file, 'r') as f:
        #     cuffcon = json.load(f)
        #     cuffcon = renamer(rename_dict,cuffcon)
        # with open(file, 'w') as f:
        #     json.dump(cuffcon, f, indent=2)
        with open(file, 'r') as f:
            cuffcon = json.load(f)
            cuffcon = descriptor(descript, cuffcon)
        with open(file, 'w') as f:
            json.dump(cuffcon, f, indent=2)
print(missing)
