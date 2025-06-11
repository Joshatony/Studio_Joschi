import random
import hashlib
import time

class SecureRNG:
    def __init__(self, seed=None):
        if seed is None:
            seed = str(time.time()).encode()
        else:
            seed = str(seed).encode()
        self.seed = seed
        self.rng = random.Random()
        self.rng.seed(int(hashlib.sha256(seed).hexdigest(), 16))

    def get_symbol(self, symbols):
        return self.rng.choice(symbols)

    def get_seed_hash(self):
        return hashlib.sha256(self.seed).hexdigest()

    def get_original_seed(self):
        return self.seed.decode(errors="ignore")
