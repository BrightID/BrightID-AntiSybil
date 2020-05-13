OUTPUT_FOLDER = './outputs/manual_attack/'
INPUT_FOLDER = './inputs/'
BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'

# Select Algorithms
SYBIL_RANK = True
SYBIL_GROUP_RANK = True
INTRA_GROUP_WEIGHT = False
WEIGHTED_SYBIL_RANK = True
GROUP_MERGE = False

# Algorithms options
ACCUMULATIVE = False
NONLINEAR_DISTRIBUTION = False
GROUP_EDGE_WEIGHT = 20
THRESHOLDS = [.36, .24, .18, .12, .06, .04, .02, .01,
              .005, .004, .003, .002, .0015, .001, .0005, 0]
