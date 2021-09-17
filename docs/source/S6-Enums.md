In the Python portions of the pipeline we use
[Enums](https://docs.python.org/3/library/enum.html)
which are “… a set of
symbolic names (members) bound to unique, constant values. Within an
enumeration, the members can be compared by identity, and the
enumeration itself can be iterated over.” Enums improve code readability
and are useful when a parameter can only assume one value from a set of
possible values.

We store our Enums in `src/utils/enums.py`. While programming in Python,
Enums are used to make interfacing with our JSON parameter input and
storage files easier. We recommend that as users expand upon ASCENT’s
functionality that they continue to use Enums, adding to existing
classes or creating new classes when appropriate. 