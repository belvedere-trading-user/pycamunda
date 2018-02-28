"""@ingroup pycamunda
@file
An injectable abstraction for common os operations.
"""
import os

class System(object):
    """An injectable abstraction of system-level operations required by the api connector.

    This includes actions such as reading files, executing system commands, etc.
    """
    #pylint: disable=no-self-use
    def is_directory(self, path):
        """Returns whether the provided path is an existing directory on the underlying system.

        @param path The path of the directory to look for.
        @returns A boolean.
        """
        return os.path.isdir(path)

    def create_directory(self, path, mode=0644, create_parents=True):
        """Creates an empty directory on the underlying system.

        @param path The path to the directory that should be created.
        @param mode The permission level that should be applied to the newly created directory.
        @param create_parents Whether any missing parent directories should also be created.
        """
        if create_parents:
            os.makedirs(path, mode=mode)
        else:
            os.mkdir(path, mode=mode)

    def list_directory(self, path, fully_qualify=True):
        """Lists the files contained within a single directory on the underlying system.

        @param path The path to the directory that should be inspected.
        @param fully_qualify A boolean specifying whether the returned files should contain a path component in addition to their file names.
        @returns A list of strings.
        """
        files = os.listdir(path)
        if fully_qualify:
            files = [self.join(path, f) for f in files]
        return files

    def is_file(self, path):
        """Returns whether the provided path is an existing file on the underlying system.

        @param path The path of the file to look for.
        @returns A boolean.
        """
        return os.path.isfile(path)

    def create_file(self, path, contents): #pylint: disable=no-self-use
        """Creates a file with the specified contents.

        @param path The path to the file that should be created.
        @param contents A string.
        """
        with open(path, 'w') as new_file:
            new_file.write(contents)

    def read_file(self, path):
        """Reads the contents of a file.

        @param path The path to the file that should be read.
        @returns A string.
        """
        with open(path, 'rb') as the_file:
            return the_file.read()

    def delete_file(self, path):
        """Deletes a file from the underlying host.

        @param path The path to the file that should be deleted.
        """
        if self.is_file(path):
            os.remove(path)

    def join(self, path, *paths):
        """Joins path components together to create a single path.

        @param path The base path.
        @param paths Path components to be appended to @p path.
        @returns A string.
        """
        return os.path.join(path, *paths)

    def get_extension(self, path):
        """Retrieves the file extension for a file path.

        @param path The path to process.
        @returns A string.
        """
        return os.path.splitext(path)[1]

    def get_environment_variable(self, key, default=None):
        """Retrieves the value of an environment variable from the current running environment.

        @param key The name of the variable to retrieve.
        @param default Optionally, the default value to be returned if @p key is unset.
        @returns A string.
        """
        return os.getenv(key, default=default)
