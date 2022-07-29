# query_criteria.json

Named file: `config/user/query_criteria/<query criteria index>.json`

## Purpose

Used to guide the Query class’s searching algorithm in the
`run()` and `_match()` methods. This is used for pulling **_Sample_**,
**_Model_**, or **_Sim_** indices for data analysis. The
`query_criteria.json` dictates if a given **_Sample_**, **_Model_**,
or **_Sim_** fit the user’s restricted parameter values ([Python Morphology Classes](../../Running_ASCENT/Usage.md#data-analysis-tools)).

## Syntax

```javascript
{
  "partial_matches": Boolean,
  "include_downstream": Boolean,
  "sample": { // can be empty, null, or omitted
  },
  "model": { // can be empty, null, or omitted
  },
  "sim": { // can be empty, null, or omitted
  },
  "indices": {
    "sample": null, Integer, or [Integer, ...],
    "model": null, Integer, or [Integer, ...],
    "sim": null, Integer, or [Integer, ...]
  }
}
```

## Properties

`"partial_matches"`: The value (Boolean) indicates whether Query should
return configuration indices for **_Sample_**, **_Model_**, or **_Sim_**
that are a partial match (i.e., a subset of the parameters were found,
but not all).

`"include_downstream"`: The value (Boolean) indicates whether Query
should return indices of downstream (**_Sample_** \> **_Model_** \>
**_Sim_**) configurations that exist if match criteria are not provided
for them.

`"sample"`: The value is a JSON Object that mirrors the path to the
parameters of interest in **_Sample_** and their value(s).

`"model"`: The value is a JSON Object that mirrors the path to the
parameters of interest in **_Model_** and their value(s).

`"sim"`: The value is a JSON Object that mirrors the path to the
parameters of interest in **_Sim_** and their value(s).

`"indices"`:

- `"sample"`: The value (null, Integer, or \[Integer, …\]) for
  explicitly desired **_Sample_** indices

- `"model"`: The value (null, Integer, or \[Integer, …\]) for explicitly
  desired **_Model_** indices

- `"sim"`: The value (null, Integer, or \[Integer, …\]) for explicitly
  desired **_Sim_** indices

Note: you can have BOTH lists of desired **_Sample_**, **_Model_**, and
**_Sim_** indices AND search criteria in one `query_criteria.json`.

## Example

```{eval-rst}
.. include:: ../../../../config/templates/query_criteria.json
   :code: javascript
```
