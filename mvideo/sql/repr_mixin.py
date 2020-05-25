class ReprMixin:
    def __repr__(self):
        args_ = ', '.join(
            f"{k}=" + (f"'{v}'" if isinstance(v, str) else str(v))
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({args_})"
