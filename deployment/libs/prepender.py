#from http://stackoverflow.com/questions/2677617/python-f-write-at-beginning-of-file


class Prepender:
    def __init__(self, fname, mode='w'):
        self.__write_queue = []
        self.__f = open(fname, mode)

    def write(self, s):
        self.__write_queue.insert(0, s)

    def close(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.__write_queue: 
            self.__f.writelines(self.__write_queue)
        self.__f.close()