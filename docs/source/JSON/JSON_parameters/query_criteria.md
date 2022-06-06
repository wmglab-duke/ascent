
# query\_criteria.json

Named file: `config/user/query_criteria/<query criteria
    index>.json`

## Purpose
Used to guide the Query class’s searching algorithm in the
    `run()` and `_match()` methods. This is used for pulling ***Sample***,
    ***Model***, or ***Sim*** indices for data analysis. The
    `query_criteria.json` dictates if a given ***Sample***, ***Model***,
    or ***Sim*** fit the user’s restricted parameter values ([S33 Text](S33-Data-analysis-tools)).

## Syntax
    ```
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

    `“partial_matches”`: The value (Boolean) indicates whether Query should
    return configuration indices for ***Sample***, ***Model***, or ***Sim***
    that are a partial match (i.e., a subset of the parameters were found,
    but not all).

    `“include_downstream"`: The value (Boolean) indicates whether Query
    should return indices of downstream (***Sample*** \> ***Model*** \>
    ***Sim***) configurations that exist if match criteria are not provided
    for them.

    `“sample”`: The value is a JSON Object that mirrors the path to the
    parameters of interest in ***Sample*** and their value(s).

    `“model”`: The value is a JSON Object that mirrors the path to the
    parameters of interest in ***Model*** and their value(s).

    `“sim”`: The value is a JSON Object that mirrors the path to the
    parameters of interest in ***Sim*** and their value(s).

    `“indices”`: 

      - `“sample”`: The value (null, Integer, or \[Integer, …\]) for
        explicitly desired ***Sample*** indices

      - `“model”`: The value (null, Integer, or \[Integer, …\]) for explicitly
        desired ***Model*** indices

      - `“sim”`: The value (null, Integer, or \[Integer, …\]) for explicitly
        desired ***Sim*** indices

    Note: you can have BOTH lists of desired ***Sample***, ***Model***, and
    ***Sim*** indices AND search criteria in one `query_criteria.json`.

## Example
    ```
    {
      "partial_matches": true,
      "include_downstream": true,
      "sample": {
        "sample": "Rat16-3"
      },
      "model": {
        "medium": {
          "proximal": {
            "length": [1000, 2000]
          }
        }
      },
      "sim": null,
      "indices": {
        "sample": null,
        "model": null,
        "sim": null
      }
    }
    ```
