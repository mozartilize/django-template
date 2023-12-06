from gunicorn.glogging import Logger as _Logger


class Logger(_Logger):
    def setup(self, cfg):
        pass