# exceptions.json

Named file: `config/system/exceptions.json`

## Purpose

The file contains a list of JSON Objects, one for each
documented pipeline exception. Note that this file is a single large
Array, so it is wrapped in square brackets, as opposed to all other
JSON files, which are wrapped in curly braces.

## Syntax 

To declare this entity in `config/system/env.json`, use the
following syntax:

```javascript
[
  {
    "code": Integer,
    "text": String
  },
  ...
]
```

## Properties

`"code"`: The value (Integer) is an identifier that enables easy reference
to a specific exception using Exceptionable’s
`self.throw(<code_index>)`. This value must be unique because the
Exeptionable class uses this value to find any given exception. We
suggest that you increment the code with each successive exception (akin
to indexing), but any number will work as long as its value is unique.

`"text"`: The value (String) is a message to the user explaining why the
pipeline failed.

## Example

See: `config/system/exceptions.json`

Note: The user should not need to change this file unless adding new
exceptions to ASCENT.
