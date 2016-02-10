"""
CallerId holds information about one end of a call.

The users of this application are interested in tuples of caller ID
number, caller ID name and sometimes an account ID (accountcode), and
it's privacy settings, both for call initiators and for call recipients.
"""
from collections import namedtuple


class CallerId(namedtuple('CallerIdBase', 'code name number is_public')):
    """
    An immutable CallerId class.

    Usage::

        caller = CallerId(name='My name', number='+311234567', is_public=True)
        caller = caller.replace(code=123456789)
    """
    def __new__(cls, code=0, name='', number=None, is_public=None):
        return super().__new__(cls, code, name, number, is_public)

    def replace(self, **kwargs):
        """
        Return a new CallerId instance replacing specified fields with
        new values.

        Args:
            **kwargs: One or more of code, name, number, is_public.

        Returns:
            CallerId: A new instance with replaced values.
        """
        # The method already exists on the namedtuple. We simply make it
        # public.
        return self._replace(**kwargs)

    def _is_public_tag(self):
        if self.is_public is None:
            return ''
        elif self.is_public:
            return ';pub'
        else:
            return ';priv'

    def __str__(self):
        return '"{}" <{}{};code={}>'.format(
            self.name.replace('\\', '\\\\').replace('"', '\\"'),
            self.number, self._is_public_tag(), self.code)
