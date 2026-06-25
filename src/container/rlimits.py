import resource

LIMIT_MAP = {
    'nofile': resource.RLIMIT_NOFILE,
    'nproc': resource.RLIMIT_NPROC,
    'memlock': resource.RLIMIT_MEMLOCK,
    'as': resource.RLIMIT_AS,
    'fsize': resource.RLIMIT_FSIZE,
    'cpu': resource.RLIMIT_CPU,
    'core': resource.RLIMIT_CORE,
}

DEFAULT_CONTAINER_LIMITS = {
    'nofile': (1024, 4096),
    'nproc': (512, 1024),
    'core': (0, 0),
}


class RlimitManager:

    def __init__(self, limits: dict[str, tuple[int, int]] | None = None):
        self.limits = dict(DEFAULT_CONTAINER_LIMITS)
        if limits:
            self.limits.update(limits)

    def set_limit(self, name: str, soft: int, hard: int):
        if name not in LIMIT_MAP:
            raise ValueError(f"Unknown rlimit: {name}. Valid: {', '.join(LIMIT_MAP)}")
        self.limits[name] = (soft, hard)

    def get_current(self, name: str) -> tuple[int, int]:
        if name not in LIMIT_MAP:
            raise ValueError(f"Unknown rlimit: {name}")
        return resource.getrlimit(LIMIT_MAP[name])

    def apply(self):
        for name, (soft, hard) in self.limits.items():
            resource.setrlimit(LIMIT_MAP[name], (soft, hard))
