import itertools
import subprocess
import os

from haddock.workflows.scoring.pdb.utils import load_structure
from haddock.workflows.scoring.config import load_parameters

param_dic = load_parameters()
fastcontact_exe = param_dic['third-party']['fastcontact_exe']


def fastcontact(pdb_f):

    felecv = .0
    fdesolv = .0
    freee = .0

    prot_dic = load_structure(pdb_f)

    for segid_x, segid_y in itertools.combinations(prot_dic, 2):

        prot_x = '{}.pdb'.format(segid_x)
        prot_y = '{}.pdb'.format(segid_y)
        open(prot_x,'w').write(''.join(prot_dic[segid_x]))
        open(prot_y, 'w').write(''.join(prot_dic[segid_y]))

        p = subprocess.Popen([fastcontact_exe, prot_x, prot_y], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.communicate()
        i, j, k = map(float, str(out[0]).split('\\n')[1].split())
        felecv += i
        fdesolv += j
        freee += k

        os.remove(prot_x)
        os.remove(prot_y)

    return felecv, fdesolv
