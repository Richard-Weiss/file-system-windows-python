class Config:
    """
    Singleton configuration class.

    This class is used to store and manage configuration settings for allowed and denied directories.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the Config class if it does not already exist.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Config: The singleton instance of the Config class.
        """
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the Config instance.

        This method sets up the allowed and denied directories lists if the instance is not already initialized.
        """
        if not hasattr(self, '_initialized'):
            self.allow = []
            self.deny = []
            self._initialized = True
