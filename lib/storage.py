import os.path

class LocalStorage(object):
    """Represents a local place where files can be obtained from and stored to."""

    def __init__(self, basepath=''):
        self.basepath = basepath

    def is_local_storage(self):
        "returns wether this storage is local (local storage uris can be open()ed directly)"
        return True

    def get_file_uri(self, file):
        return os.path.join(self.basepath, file) if self.basepath else file

    def get_file(self, file):
        "returns a file-like object for reading the given file"
        return open(self.get_file_uri(file), 'rb')

    def get_file_list(self, path='', filter=None):
        "returns an iterator with the files in this storage, prefixed by the given path and passing the given filter."
        filedir = os.path.join(self.basepath, path) if path else self.basepath
        return [x for x in os.listdir(filedir) if filter(x)] if filter else os.listdir(filedir)

    def open_for_writing(self, file, **kwd):
        "returns a file-like object for writing to a given file in the storage"
        return open(self.get_file_uri(file), 'wb')

    def put_file(self, file, filedata, acl=None):
        "stores the given filedata into the given file"
        with open(self.get_file_uri(file), 'wb') as fout:
            fout.write(filedata)

    def put_file_fd(self, file, fd, acl=None):
        "stores the data read from the file-like object fd into the given file"
        self.put_file(file, fd.read(), acl=acl)

    def put_file_path(self, file, filepath, acl=None):
        "stores the data read from the local file in filepath into the given file"
        with open(filepath, 'rb') as fd:
            self.put_file_fd(file, fd, acl=acl)

    def exists(self, file=''):
        return os.path.exists(self.get_file_uri(file) if file else self.basepath)

    def __repr__(self):
        return '<'+self.__class__.__name__ + ' basepath:'+ repr(self.basepath) +'>'
