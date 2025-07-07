"""Compare two /samples directories.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import difflib
import filecmp
import itertools
import json
import os
import shutil
import time

import numpy as np


def _tmp_cleanup():
    if os.path.exists('diff/tmp'):
        shutil.rmtree('diff/tmp')


def get_from_to_lines(f_left: str, f_right: str):
    """Get formatted difference between two files.

    :param f_left: left file path
    :param f_right: right file path
    :return: different lines in left file, diff lines in right file, unreadable boolean
    """
    try:
        with open(f_left) as lf:
            from_lines = lf.readlines()
        with open(f_right) as rf:
            to_lines = rf.readlines()
    except UnicodeDecodeError:
        # not a plaintext file
        return [], [], True

    return from_lines, to_lines, False


def order_dict(unordered_dict: dict) -> dict:
    """Order dictionary recursively.

    :param unordered_dict: dictionary to be ordered
    :return: dictionary ordered by key
    """
    ordered_dict = {}
    for k, v in sorted(unordered_dict.items()):
        if isinstance(v, dict):
            ordered_dict[k] = order_dict(v)
        else:
            ordered_dict[k] = v
    return ordered_dict


def set_key_null(f_dict: dict, key: str or list[str]):
    """Set json keys to null to ignore comparison.

    :param f_dict: dictionary from json file
    :param key: key to set to null. Either string or list of strings for nested key.
    """
    if isinstance(key, list):
        # if key is a list, it specifies a dictionary tree
        if len(key) > 1:
            set_key_null(f_dict[key[0]], key[1:])
        else:
            f_dict[key[0]] = None
    else:
        f_dict[key] = None


def sort_ignored_jsons(f_left: str, f_right: str, ignored_keys: list):
    """Set keys in ignored_keys to null in both files and sort the dicts by key.

    :param f_left: left file path
    :param f_right: right file path
    :param ignored_keys: list of keys to ignore
    :return: different lines in left file, diff lines in right file, unreadable boolean
    """
    with open(f_left) as lf:
        left_dict = json.load(lf)
    with open(f_right) as rf:
        right_dict = json.load(rf)
    for k in ignored_keys:
        set_key_null(left_dict, k.split('/'))
        set_key_null(right_dict, k.split('/'))

    left_dict = order_dict(left_dict)
    right_dict = order_dict(right_dict)

    # make temporary files for plaintext comparison instead of modifying original files
    os.makedirs('diff/tmp', exist_ok=True)
    with open('diff/tmp/left.json', 'w') as lf:
        json.dump(left_dict, lf, indent=2)
    with open('diff/tmp/right.json', 'w') as rf:
        json.dump(right_dict, rf, indent=2)

    return get_from_to_lines('diff/tmp/left.json', 'diff/tmp/right.json')


def save_compare(dcmp: filecmp.dircmp, root: str, ignore_dict: dict):
    """Save a diff list for files in one directory.

    :param dcmp: dircmp object for folder comparison
    :param root: directory to which diff files will be saved
    :param ignore_dict: dictionary of file patterns and keys to ignore
    :return: boolean, True if differences were found, False if all files are equivalent
    """
    diff_ignored = []
    diff_vals = []
    for df in dcmp.diff_files:
        max_diff = None
        f_left = os.path.join(dcmp.left, df)
        f_right = os.path.join(dcmp.right, df)
        ignored_keys = ignore_dict[df]['keys'] if df in ignore_dict else []

        if os.path.splitext(df)[1] == '.json':
            from_lines, to_lines, ignored = sort_ignored_jsons(f_left, f_right, ignored_keys)
        else:
            # else plaintext comparison
            from_lines, to_lines, ignored = get_from_to_lines(f_left, f_right)

        if not ignored:  # ignored=True would mean that files are not plaintext
            diff_txt = list(difflib.context_diff(from_lines, to_lines, fromfile=f_left, tofile=f_right, n=1))
            if len(diff_txt) == 0:
                ignored = True  # ignored=True means that ignored_keys were different, but otherwise files equivalent
            else:
                df_name, df_ext = os.path.splitext(df)

                # Write different lines to file
                with open(os.path.join(root, df_name) + '_diff.txt', 'w') as f:
                    if len(ignored_keys) > 0:
                        f.write("Ignored keys: " + " ".join(ignored_keys))
                    f.writelines(diff_txt)

                if df_ext in ['.dat', '.txt']:
                    left_data = None
                    try:
                        left_data = np.loadtxt(f_left, dtype=float, comments=('#', '%'))
                        right_data = np.loadtxt(f_right, dtype=float, comments=('#', '%'))

                    except ValueError:
                        # Cannot cast data to float
                        try:
                            left_data = np.loadtxt(f_left, dtype=float, comments=('#', '%'), skiprows=1)
                            right_data = np.loadtxt(f_right, dtype=float, comments=('#', '%'), skiprows=1)
                        except ValueError:
                            max_diff = None

                    if left_data is not None:
                        if left_data.size != right_data.size:
                            max_diff = '!='  # array sizes not equal
                        else:
                            diff_val = right_data - left_data
                            try:
                                len(diff_val)
                            except TypeError:
                                diff_val = [diff_val]
                            np.savetxt(os.path.join(root, df_name) + '_diff.dat', diff_val)
                            max_diff = np.abs(diff_val).max()

        diff_ignored.append(ignored)
        diff_vals.append(max_diff)

    if 'test_ignore' in ignore_dict:
        left_only = list(filter(lambda x: x not in ignore_dict['test_ignore'], dcmp.left_only))
    else:
        left_only = dcmp.left_only

    if 'sample_ignore' in ignore_dict:
        right_only = list(filter(lambda x: x not in ignore_dict['sample_ignore'], dcmp.right_only))
    else:
        right_only = dcmp.right_only

    diff_files = list(itertools.compress(dcmp.diff_files, [not db for db in diff_ignored]))

    is_diff = len(diff_files) > 0 or len(left_only) > 0 or len(right_only) > 0

    if is_diff:
        diff_vals = list(itertools.compress(diff_vals, [not db for db in diff_ignored]))
        diff_file_val = [f'{df} | {pd}' for df, pd in zip(diff_files, diff_vals)]
        with open(os.path.join(root, 'file_compare.txt'), 'w') as f:
            f.write(f"Directory comparison between {dcmp.left} and {dcmp.right}\n")
            f.write("\nDifferent files | Max Diff:\n\t")
            f.writelines("\n\t".join(diff_file_val))
            f.write("\nIgnored files or identical with ignored keys:\n\t")
            f.writelines("\n\t".join(dcmp.funny_files))
            f.writelines("\n\t".join(itertools.compress(dcmp.diff_files, diff_ignored)))
            f.write("\nSame files:\n\t")
            f.writelines("\n\t".join(dcmp.same_files))
            f.write("\nCommon folders:\n\t")
            f.writelines("\n\t".join(dcmp.common_dirs))
            f.write(f"\n{dcmp.left}-only files:\n\t")
            f.writelines("\n\t".join(left_only))
            f.write(f"\n{dcmp.right}-only files:\n\t")
            f.writelines("\n\t".join(right_only))

    return is_diff


def recurse_compare(dcmp: filecmp.dircmp, root: str, ignore_dict: dict):
    """Recursively compare two folders and save the file diffs to txt files.

    :param dcmp: dircmp object for folder comparison
    :param root: directory to which diff files will be saved
    :param ignore_dict: dictionary of file patterns and keys to ignore
    :return: boolean, True if differences were found, False if all files are equivalent
    """
    is_diff = save_compare(dcmp, root, ignore_dict)

    sub_diff = []
    for subdir, sdcmp in dcmp.subdirs.items():
        sub_cmpdir = os.path.join(root, subdir)
        os.makedirs(sub_cmpdir, exist_ok=True)
        sub_diff.append(recurse_compare(sdcmp, sub_cmpdir, ignore_dict))
        if len(os.listdir(sub_cmpdir)) == 0:
            shutil.rmtree(sub_cmpdir)

    return is_diff or any(sub_diff)


def compare_directories(dir_left: str, dir_right: str, ignore_dict: dict):
    """Compare two directories while ignoring specific files and json keys.

    :param dir_left: "left" directory to compare
    :param dir_right: directory to which diff files will be saved
    :param ignore_dict: dictionary of file patterns and keys to ignore
    :return: boolean, True if differences were found, False if all files are equivalent
    """
    dir_left = os.path.normpath(dir_left)
    dir_right = os.path.normpath(dir_right)
    cmp_dir = 'diff/' + '_'.join(dir_left.split(os.sep)) + '-' + '_'.join(dir_right.split(os.sep))
    if os.path.exists(cmp_dir):
        shutil.rmtree(cmp_dir)
    time.sleep(1)
    os.makedirs(cmp_dir)
    ignore = ignore_dict['ignore'] if 'ignore' in ignore_dict else None
    filecmp.clear_cache()
    dir_cmp = filecmp.dircmp(dir_left, dir_right, ignore=ignore)
    print(f'Comparing {dir_left} to {dir_right}')
    filecmp.clear_cache()
    is_diff = recurse_compare(dir_cmp, cmp_dir, ignore_dict)
    if is_diff:
        print(f'\tDifferences between {dir_left} and {dir_right}')
        print(f'\tSee {cmp_dir} for details')
    else:
        print(f'\tNo differences between {dir_left} and {dir_right}')

    _tmp_cleanup()

    return is_diff


def run(args):
    """Create directory comparison between two ASCENT /samples directories.

    :param args: command line arguments
    :return: boolean, True if differences were found, False if all files are equivalent
    """
    assert len(args.sample_indices) == 2, 'Script can only compare two sample indices'
    comp_dirs = ['samples/' + str(si) for si in args.sample_indices]
    return compare_directories(*comp_dirs, ignore_dict={})


def main():
    """Create directory comparison between first two ASCENT /samples."""
    samps = os.listdir('samples')
    with open('tests/integration/test_ignore.json') as f:
        default_ignore = json.load(f)
    is_diff = compare_directories('samples/' + samps[0], 'samples/' + samps[1], default_ignore['full_test'])
    if not is_diff:
        print("Directories are the same")


if __name__ == '__main__':
    main()
