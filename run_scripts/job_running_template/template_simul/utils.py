#!/usr/bin/env python
import os
import shutil


def safe_makedir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def check_exist(filename):
    if not os.path.exists(filename):
        raise ValueError("Path not exists: %s" % filename)


def read_txt_into_list(filename):
    with open(filename, "r") as f:
        return [x.rstrip("\n") for x in f]


def dump_list_to_txt(filename, content):
    with open(filename, 'w') as f:
        for line in content:
            f.write("%s\n" % line)


def cleantree(folder):
    if not os.path.exists(folder):
        return
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception, e:
            print e


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(src):
        raise ValueError("Src dir not exists: %s" % src)
    if not os.path.exists(dst):
        raise ValueError("Dest dir not exists: %s" % dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def copyfile(origin_file, target_file, verbose=True):
    if not os.path.exists(origin_file):
        raise ValueError("No such file: %s" % origin_file)

    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    if verbose:
        print("Copy file:[%s --> %s]" % (origin_file, target_file))
    shutil.copy2(origin_file, target_file)


def get_permission():
    answer = raw_input("[Y/n]:")
    if answer == "Y":
        return True
    elif answer == "n":
        return False
    else:
        raise ValueError("answer incorrect: %s" % answer)
