from source import CMTSource
import argparse
from copy import deepcopy
import sqlite3
import os


def validate_cmt(cmt):
    if cmt.depth_in_m < 0.0:
        raise ValueError("Depth(m): %f < 0" % (cmt.depth_in_m))

    if cmt.latitude < -90.0:
        cmt.latitude += 90.
    elif cmt.latitude > 90.0:
        cmt.latitude -= 90.

    if cmt.longitude < -180.0:
        cmt.longitude += 180.
    elif cmt.longitude > 180.0:
        cmt.longitude -= 180.


def perturb_one_var(pert_type, origin_cmt, pert_value, outputdir):
    cmt = deepcopy(origin_cmt)
    if pert_type in ['m_rr', 'm_tt', 'm_pp', 'm_rt', 'm_rp', 'm_tp']:
        # if perturb moment tensor, set all moment tensor to zero
        cmt.m_rr = 0.0; cmt.m_tt=0.0; cmt.m_pp = 0.0
        cmt.m_rt = 0.0; cmt.m_rp = 0.0; cmt.m_tp = 0.0
        setattr(cmt, pert_type, pert_value)
    elif pert_type in ['depth_in_m', 'latitude', 'longitude']:
        attr = getattr(cmt, pert_type)
        setattr(cmt, pert_type, attr+pert_value)

    validate_cmt(cmt)

    suffix_dict = {'m_rr':"Mrr", 'm_tt':"Mtt", 'm_pp':"Mpp", 'm_rt':"Mrt", 
                   'm_rp':"Mrp", 'm_tp':"Mtp", "depth_in_m":"dep", 
                   "latitude":"lat", "longitude":"lon"}
    suffix = suffix_dict[pert_type]
    outputfn = os.path.join(outputdir, "%s_%s" % (cmt.eventname, suffix))
    cmt.write_CMTSOLUTION_file(outputfn)


def perturb_cmt(input_cmtfile, output_dir=".", dmoment_tensor=None, 
                dlongitude=None, dlatitude=None, ddepth_km=None):

    cmt = CMTSource.from_CMTSOLUTION_file(input_cmtfile)

    if dmoment_tensor is not None:
        pert_type_list = ['m_rr', 'm_tt', 'm_pp', 'm_rt', 'm_rp', 'm_tp']
        for pert_type in pert_type_list:
            perturb_one_var(pert_type, cmt, dmoment_tensor, output_dir)

    if dlongitude is not None:
        perturb_one_var("longitude", cmt, dlongitude, output_dir)

    if dlatitude is not None:
        perturb_one_var("latitude", cmt, dlatitude, output_dir)

    if ddepth_km is not None:
        perturb_one_var("depth_in_m", cmt, ddepth_km*1000.0, output_dir)


def gen_cmt_wrapper(input_cmt, dmoment_tensor=None,ddepth=None,
            dlatitude=None, dlongitude=None, output_dir="."):                                                
    if not os.path.exists(output_dir):                                          
        os.makedirs(output_dir)                                                 
                                                                                
    perturb_cmt(input_cmt, output_dir=output_dir, 
                dmoment_tensor=dmoment_tensor,       
                dlongitude=dlongitude, dlatitude=dlatitude,                     
                ddepth_km=ddepth)


if __name__ == '__main__':

    with open("config.yaml") as fh:
        config = yaml.load(fh)

    dmoment_tensor = config["dmoment_tensor"]
    ddepth = config["ddepth"]
    dlatitude = config["dlatitude"]
    dlongitude = config["dlongitude"]
                                                                                
    cmtdir = "cmtfile"                                                    
    cmtfiles = glob.glob(os.path.join(cmtdir, "*"))
    print("Number of CMT files: %d" % len(cmtfiles))
    
    for _file in cmtfiles:                                                     
        gen_cmt_wrapper(_file, dmoment_tensor=dmoment_tensor, ddepth=ddepth,
                dlatitude=dlatitude, dlongitude=dlongitude)
