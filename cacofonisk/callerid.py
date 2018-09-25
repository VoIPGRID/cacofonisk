from collections import namedtuple


class CallerId(namedtuple('CallerIdBase', 'name num')):
    """
    CallerId holds immutable information about one end of a call.

    The users of this application are interested in tuples of caller ID number,
    caller ID name and sometimes an account ID (accountcode), and it's privacy
    settings, both for call initiators and for call recipients.

    Usage::

        caller = CallerId(name='My name', number='+311234567', is_public=True)
        caller = caller.replace(code=123456789)
    """

    def __new__(cls, name='', num=''):
        if name == '<unknown>':
            name = ''

        if num == '<unknown>':
            num = ''

        return super().__new__(cls, name, str(num))

    def replace(self, **kwargs):
        """
        Create a copy of this CallerId with specified changes.

        Args:
            **kwargs: One or more of code, name, number, is_public.

        Returns:
            CallerId: A new instance with replaced values.
        """
        if 'name' in kwargs and kwargs['name'] == '<unknown>':
            kwargs['name'] = ''

        if 'num' in kwargs and kwargs['num'] == '<unknown>':
            kwargs['num'] = ''

        return self._replace(**kwargs)
