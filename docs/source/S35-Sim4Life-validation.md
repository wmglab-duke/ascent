# Sim4Life validation

We designed test simulations to verify ASCENT’s activation thresholds.
The verifications were performed by The Foundation for Research
Technologies in Society (IT’IS) with the
[Sim4Life](https://zmt.swiss/sim4life/)
(Zurich, Switzerland) simulation platform. Running the following
simulations required modification of the Sim4Life solver to implement
the required electrical anisotropy of tissue conductivities and the
boundary condition to represent the thin layer approximation used to
model the perineurium.

## Monofascicular rat nerve model

We validated activation thresholds for fibers seeded in a model of a rat
cervical vagus nerve instrumented with a bipolar cuff electrode (Figure A and B).

![Inline image](uploads/c4e1209883229cff32a21cdf0999e0de/Picture2_CrossSection1.jpg)

Figure A. Raw histology image (r.tif), segmented histology (i.tif), and scalebar (s.tif) of a rat cervical vagus nerve sample that served as inputs to define the cross section of the nerve in the FEM.

![Inline image](uploads/e276681caea4240d2ef5d78de21ab87c/Picture3_Cuff1.jpg)

Figure B. FEM of a rat cervical vagus nerve sample instrumented with a bipolar cuff electrode.

The conductivity values applied to the rat cervical FEM are provided in
Table A, and the boundary conditions applied are provided in
Table B.

Table A. Conductivity values for FEM of rat cervical vagus nerve. These values
were also used in multifascicular nerve model and human model
verifications.

<table border="1" style="padding:5px">
<thead>
<tr class="header">
<th><strong>Parameter</strong></th>
<th><strong>Application</strong></th>
<th><strong>Resistivity</strong> Ω-m</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Endoneurium</td>
<td align="center"style="vertical-align:middle" >Within each fascicle</td>
<td align="center"style="vertical-align:middle" ><p>1.75 longitudinal</p>
<p>6 radial (rat and human)</p>
<p>12 radial (multifascicular dummy model)</p></td>
</tr>
<tr class="even">
<td align="center"style="vertical-align:middle" >Saline</td>
<td align="center"style="vertical-align:middle" >Cylindrical shell between the nerve and cuff</td>
<td align="center"style="vertical-align:middle" >1/1.76</td>
</tr>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Platinum</td>
<td align="center"style="vertical-align:middle" >For both contacts</td>
<td align="center"style="vertical-align:middle" >1/(9.43*10<sup>6</sup>)</td>
</tr>
<tr class="even">
<td align="center"style="vertical-align:middle" >Silicone</td>
<td align="center"style="vertical-align:middle" >For electrode body</td>
<td align="center"style="vertical-align:middle" >10<sup>12</sup></td>
</tr>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Muscle</td>
<td align="center"style="vertical-align:middle" >Used for the surrounding “medium”: Everything outside of the nerve and cuff, other than the saline layer between the nerve and cuff</td>
<td align="center"style="vertical-align:middle" ><p>1/0.35 longitudinal</p>
<p>1/0.086 radial</p></td>
</tr>
<tr class="even">
<td align="center"style="vertical-align:middle" >Epineurium</td>
<td align="center"style="vertical-align:middle" >Within the nerve around each fascicle</td>
<td align="center"style="vertical-align:middle" >6.3</td>
</tr>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Encapsulation</td>
<td align="center"style="vertical-align:middle" >Between cuff and nerve, and immediately surrounding cuff</td>
<td align="center"style="vertical-align:middle" >6.3</td>
</tr>
</tbody>
</table>

Table B. Boundary conditions used in FEM of rat cervical vagus nerve,
multifascicular dummy nerve, and human cervical vagus nerve.

<table border="1" style="padding:5px">
<thead>
<tr class="header">
<th><strong>Parameter</strong></th>
<th><strong>Setting</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Current conservation</td>
<td align="center"style="vertical-align:middle" >All domains</td>
</tr>
<tr class="even">
<td align="center"style="vertical-align:middle" >Initial condition</td>
<td align="center"style="vertical-align:middle" >V=0 (all domains)</td>
</tr>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Perineurium (sides of each fascicle)</td>
<td align="center"style="vertical-align:middle" ><p>Modeled as contact impedance</p>
<p>1149 Ω-m * 0.03 * d<sub>fasc</sub>[m]</p></td>
</tr>
<tr class="even">
<td align="center"style="vertical-align:middle" >Ground (all outer boundaries of the model)</td>
<td align="center"style="vertical-align:middle" >V = 0</td>
</tr>
<tr class="odd">
<td align="center"style="vertical-align:middle" >Point current source (one in each contact)</td>
<td align="center"style="vertical-align:middle" ><p>-1 mA</p>
<ul>
<p>1 mA</p></td>
</ul></td>
</tr>
</tbody>
</table>

We compared thresholds for 100 5.7 µm myelinated axons (MRG model)
seeded in the cross section of the nerve in response to a single 100 µs
duration monophasic rectangular pulse. The differences in thresholds
between ASCENT and IT’IS model implementations was \<4.2% for all
fibers, demonstrating strong agreement (Figure C).

![Inline image](uploads/3209b7b1f369a70a973385b635c801c9/Picture4.jpg)

Figure C. Comparison of activation thresholds for the rat cervical vagus nerve implementation in ASCENT and Sim4Life.

## Multifascicular dummy nerve model

We validated activation thresholds for fibers seeded in a
multifascicular dummy nerve instrumented with a bipolar cuff electrode
(Figure D and E). The segmented histology was created using
our `mock_morphology_generator.py` script ([S12 Text](S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology)).

![Inline image](uploads/2869942c6f0a8197e76ff97b8ad0133b/Picture5.jpg)

Figure D. Mock morphology inputs to the define tissue boundaries for a multifascicular dummy nerve for validation with Sim4Life. Scale bar is 100 µm long. The nerve is a perfect circle (diameter = 250 µm, centered at (x,y)=(0,0) µm). The inners are also perfect circles: (1) diameter = 50 µm, centered at (x,y)=(40,50) µm, (2) diameter = 60 µm, centered at (x,y)=(-50,0) µm, and (3) diameter = 80 µm, centered at (x,y)=(20,-60) µm.

![Inline image](uploads/d4f2a7230a6f0faab591489c9348ed94/Picture6.jpg)

Figure E. FEM of a multifascicular nerve sample instrumented with a bipolar cuff electrode.

The conductivity values applied to multifascicular nerve sample finite
element model are provided in Table A, and the boundary conditions
applied are provided in Table B.

We seeded a single 5.7 µm diameter fiber in the center of each fascicle.
Between the ASCENT and IT’IS implementations, there was less than a 3%
difference in threshold to a single 100 µs duration monophasic
rectangular pulse.

## Multifascicular human nerve model

We validated activation thresholds for fibers seeded in a
multifascicular human cervical vagus nerve instrumented with a LivaNova
bipolar cuff electrode (Figure F and G). The segmented
histology was created using Nikon NIS-Elements.

![Inline image](uploads/67640d7375fb580ad81d634bc6a35a3e/Picture7.jpg)

Figure F. Raw histology image (r.tif), segmented inners (i.tif), segmented nerve (n.tif), and scale bar (s.tif) of a human cervical vagus nerve sample that served as inputs to define the cross section of the nerve in the FEM for validation with Sim4Life.

![Inline image](uploads/df72ab32fc2b5f2b5376152462bdbeab/Picture8.jpg)

Figure G. FEM of a human cervical vagus nerve sample instrumented with a LivaNova cuff electrode.

The conductivity values applied to the human cervical vagus nerve sample
finite element model are provided in Table A, and the boundary
conditions applied are provided in Table B.

We seeded 5.7 µm diameter fibers in each fascicle. Between the ASCENT
and IT’IS implementations, there was less than 2.5% difference to a
single 100 µs duration monophasic rectangular pulse.
