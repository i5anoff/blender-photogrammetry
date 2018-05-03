import os
import re
import subprocess
import shutil
import platform


def bundle2pmvs(bin_path, bundle_path, target_dir, pmvs_options):
    print('bundle2pmvs({}, {}, {})'.format(bin_path, bundle_path, target_dir))
    ext = '.exe' if platform.system().lower() == 'windows' else ''
    
    os.chdir(os.path.dirname(bundle_path))
    subprocess.call([os.path.join(bin_path, 'Bundle2PMVS{}'.format(ext)), 'list.txt', os.path.basename(bundle_path), target_dir, ])
    subprocess.call([os.path.join(bin_path, 'RadialUndistort{}'.format(ext)), 'list.txt', os.path.basename(bundle_path), target_dir, ])

    def mkdir(path):
        if not os.path.exists(path):
            os.mkdir(path)

    mkdir(os.path.join(target_dir, 'models'))
    mkdir(os.path.join(target_dir, 'txt'))
    mkdir(os.path.join(target_dir, 'visualize'))

    with open(os.path.join(target_dir, 'list.rd.txt'), 'r') as f:
        images = f.readlines()

    # copy 00000000.txt to txt\00000000.txt
    # copy image.rd.jpg to visualize\00000000.jpg

    # v0.3 format
    #int_format = '{:0>4}'

    # v0.4 format
    int_format = '{:0>8}'

    for i, path in enumerate(images):
        shutil.move(
            os.path.join(target_dir, (int_format + '.txt').format(i)),
            os.path.join(target_dir, 'txt', (int_format + '.txt').format(i)))
        shutil.move(
            os.path.join(target_dir, '{}.rd.jpg'.format(os.path.basename(os.path.splitext(path)[0]))),
            os.path.join(target_dir, 'visualize', (int_format + '.jpg').format(i)))

    # rewrite list.txt to include path to visualize\00000000.jpg
    with open(os.path.join(target_dir, 'list.rd.txt'), 'w+') as f:
        f.writelines([('visualize\\' + int_format + '.jpg\n').format(i) for i, data in enumerate(images)])

    # rewrite pmvs_options.txt to skip vis.dat as we won't be using cmvs here
    pmvs_options.update({'useVisData': 0})
    pattern = re.compile(r'^([^\s]+)\s')
    with open(os.path.join(target_dir, 'pmvs_options.txt'), 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match and match.group(1) in pmvs_options:
                lines[i] = '{key} {value}\n'.format(key=match.group(1), value=pmvs_options[match.group(1)])
    
    options = os.path.join(target_dir, 'reconstruction')
    with open(options, 'w+') as f:
        f.writelines(lines)
    return options


def pmvs(bin_path, option_path):
    # if linux, set:
    # LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:bin_path && export LD_LIBRARY_PATH
    print('pmvs({})'.format(option_path))
    os.chdir(os.path.dirname(option_path))

    ext = '.exe' if platform.system().lower() == 'windows' else ''
    subprocess.call([os.path.join(bin_path, 'pmvs2{}'.format(ext)), '.{}'.format(os.sep), os.path.basename(option_path), ])


def prepare():
    """
    :returns: {
        'trackers': { 
            id<int>: {
                'co': (x, y, z),
                'rgb': (r, g, b),
            }
        },
        'cameras': {
            id<int>: {
                'filename': str,
                'f': float,
                'k': (k1, k2, k3),
                'c': (x, y, z),  # real world coord
                't': (x, y, z),  # pmvs transformed translation
                'R': ((r00, r01, r02),
                      (r10, r11, r12),
                      (r20, r21, r22)),
                'trackers': {
                    id<int>: (x, y),
                }
            }
        }
    }
    """
    pass
