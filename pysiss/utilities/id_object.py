""" file: objects.py (pysiss.utilities)

    description: Some basic metaclasses etc for defining pysiss classes
"""

import uuid


class id_object(object):

    """ A mixin class to implement UUID comparisons for child classes

        This metaclass generates a UUID for a class at initialization,
        and defines the class __eq__ method to use this UUID.
    """

    def __init__(self, name, *args, **kwargs):
        super(id_object, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, name)

    def __eq__(self, other):
        """ Equality test

            Class instances are equal if their UUIDs match
        """
        return self.uuid == other.uuid
