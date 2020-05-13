OUTPUT_FOLDER = './outputs/attacks/'
INPUT_FOLDER = './inputs/'
BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'

# Select Attacks
ONE_ATTACKER_TARGETING_SEEDS = True
ONE_ATTACKER_TARGETING_TOP_NODES = True
ONE_ATTACKER_TARGETING_RANDOM_NODES = True
ONE_ATTACKER_GROUP_TARGET_ATTACK = True
ONE_SEED_AS_ATTACKER = True
ONE_HONEST_AS_ATTACKER = True
ONE_GROUP_TARGETING_SEEDS = True
ONE_GROUP_TARGETING_TOP_NODES = True
ONE_GROUP_TARGETING_RANDOM_NODES = True
ONE_GROUP_GROUP_TARGET_ATTACK = True
ONE_GROUP_OF_SEEDS_AS_ATTACKER = True
ONE_GROUP_OF_HONESTS_AS_ATTACKER = True
N_GROUPS_TARGETING_SEEDS = True
N_GROUPS_TARGETING_TOP_NODES = True
N_GROUPS_TARGETING_RANDOM_NODES = True
N_GROUPS_OF_SEEDS_AS_ATTACKER = True
N_GROUPS_OF_HONESTS_AS_ATTACKER = True

# Attacks options
N_TARGETS = 20
N_SYBILS = 50
N_ATTACKERS = 20
N_STITCHES = 0
N_GROUPS = 100
N_UNFAITHFUL_SEEDS = 5
N_UNFAITHFUL_HONESTS = 20

# Select Algorithms
SYBIL_RANK = False
SYBIL_GROUP_RANK_V1 = True
SYBIL_GROUP_RANK_V2 = False
SYBIL_GROUP_RANK = True
INTRA_GROUP_WEIGHT = False
WEIGHTED_SYBIL_RANK = False
GROUP_MERGE = False

# Algorithms options
ACCUMULATIVE = False
NONLINEAR_DISTRIBUTION = False
GROUP_EDGE_WEIGHT = 20
THRESHOLDS = [.36, .24, .18, .12, .06, .04, .02, .01,
              .005, .004, .003, .002, .0015, .001, .0005, 0]