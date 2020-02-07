def compute_cuff_shift(self, model_config: dict, sample: Sample, sample_config: dict):

    # add temporary model configuration
    self.add(SetupMode.OLD, Config.MODEL, model_config)
    self.add(SetupMode.OLD, Config.SAMPLE, sample_config)

    # fetch nerve mode
    nerve_present: NerveMode = self.search_mode(NerveMode, Config.SAMPLE)

    # fetch cuff config
    cuff_config: dict = self.load(os.path.join("config", "system", "cuffs", model_config['cuff']['preset']))

    # fetch 1-2 letter code for cuff (ex: 'CT')
    cuff_code: str = cuff_config['code']

    # fetch radius buffer string (ex: '0.003 [in]')
    cuff_r_buffer_str: str = [item["expression"] for item in cuff_config["params"]
                              if item["name"] == '_'.join(['thk_medium_gap_internal', cuff_code])][0]

    # calculate value of radius buffer in micrometers (ex: 76.2)
    cuff_r_buffer: float = Quantity(
        Quantity(
            cuff_r_buffer_str.translate(cuff_r_buffer_str.maketrans('', '', ' []')),
            scale='m'
        ),
        scale='um'
    ).real  # [um] (scaled from any arbitrary length unit)

    # get center and radius of nerve's min_bound circle
    nerve_copy = deepcopy(
        sample.slides[0].nerve
        if nerve_present == NerveMode.PRESENT
        else sample.slides[0].fascicles[0].outer
    )

    nerve_copy.down_sample(DownSampleMode.KEEP, 20)
    x, y, r_bound = nerve_copy.smallest_enclosing_circle_naive()

    # calculate final necessary radius by adding buffer
    r_f = r_bound + cuff_r_buffer

    # fetch boolean for cuff expandability
    expandable: bool = cuff_config['expandable']

    # check radius iff not expandable
    if not expandable:
        r_i_str: str = [item["expression"] for item in cuff_config["params"]
                        if item["name"] == '_'.join(['R_in', cuff_code])][0]
        r_i: float = Quantity(
            Quantity(
                r_i_str.translate(r_i_str.maketrans('', '', ' []')),
                scale='m'
            ),
            scale='um'
        ).real  # [um] (scaled from any arbitrary length unit)

        if not r_f <= r_i:
            self.throw(51)
    else:  # expandable
        # get initial cuff radius
        r_i_str: str = [item["expression"] for item in cuff_config["params"]
                        if item["name"] == '_'.join(['r_cuff_in_pre', cuff_code])][0]
        r_i: float = Quantity(
            Quantity(
                r_i_str.translate(r_i_str.maketrans('', '', ' []')),
                scale='m'
            ),
            scale='um'
        ).real  # [um] (scaled from any arbitrary length unit)

    # fetch initial cuff rotation (convert to rads)
    theta_i = cuff_config.get('angle_to_contacts_deg') * 2 * np.pi / 360

    # angle to center of circle from origin
    theta_c = np.arctan2(y, x)  # TODO this is probably wrong

    # fetch cuff rotation mode
    cuff_rotation_mode: CuffRotationMode = self.search_mode(CuffRotationMode, Config.MODEL)

    # initialize final rotation
    theta_f: float = None
    if cuff_rotation_mode == CuffRotationMode.MANUAL:
        theta_f = theta_i
    else:  # cuff_rotation_mode == CuffRotationMode.AUTOMATIC
        theta_f = ((r_i / r_f) * theta_i) - theta_c

        # remove sample config
    self.remove(Config.SAMPLE)

    # remove (pop) temporary model configuration
    model_config = self.remove(Config.MODEL)
    model_config['cuff']['rotate']['ang'] = (2 * np.pi - theta_c) * 360 / (2 * np.pi)  # theta_f * 360 / (2 * np.pi)
    model_config['cuff']['shift']['x'] = x + (r_f - r_i) * np.cos(theta_i - theta_c)
    model_config['cuff']['shift']['y'] = y + (r_f - r_i) * np.sin(theta_i - theta_c)

    return model_config