# Implementations of clinically used cuff electrodes

## LivaNova helical cuff electrode
We implemented the LivaNova helical cuff electrodes used clinically to treat patients with epilepsy and they are included in 'config/system/cuffs/'. Each cuff includes a description of it's unique elements in the `"description"` field:
- `LivaNova2000_v2.json`
- `LivaNova2000_v2.json`
- `LivaNova2000_v2_common_fill.json`
- `LivaNova3000_v2_common_fill.json`
- `LivaNovaAdaptiveDiam_v2_acute.json`
- `LivaNovaAdaptiveDiam_v2_chronic.json`

The dimensions used for the LivaNova helical cuffs are based on CAD files and technical drawings shared with the Grill Lab by LivaNova PLC as part of a contractual research agreement. The files themselves are proprietary and cannot be shared.

Modeling work which used the above cuff JSON files is published in
([Davis et al., 2023](https://doi.org/10.1088/1741-2552/acc42b), [Musselman et al., 2023](https://doi.org/10.1088/1741-2552/acda64)). Each paper has associated datasets
published on sparc.science and the datasets are cited in the data availability statement of each paper.

## ImThera six-contact cuff electrode
We implemented the ImThera six-contact cuff electrode used clinically to treat sleep apnea and it is included in `config/system/cuffs/`:
- `ImThera_flip_100.json`

The dimensions used for the ImThera cuff are based on technical drawings shared with the Grill Lab by LivaNova PLC as part of a contractual research agreement. The files themselves are proprietary and cannot be shared.

Modeling work which used the `ImThera_flip_100.json` file is published in
([Blanz et al., 2023](https://doi.org/10.1088/1741-2552/acb3fd)).
