ASCENT Validation
=================

Sim4Life validation
-------------------

We designed test simulations to verify ASCENT’s activation thresholds.
The verifications were performed by The Foundation for Research
Technologies in Society (IT’IS) with the
`Sim4Life <https://zmt.swiss/sim4life/>`__ (Zurich, Switzerland)
simulation platform. Running the following simulations required
modification of the Sim4Life solver to implement the required electrical
anisotropy of tissue conductivities and the boundary condition to
represent the thin layer approximation used to model the perineurium.

Monofascicular rat nerve model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We validated activation thresholds for fibers seeded in a model of a rat
cervical vagus nerve instrumented with a bipolar cuff electrode (Figure
A and B).

.. figure:: uploads/c4e1209883229cff32a21cdf0999e0de/Picture2_CrossSection1.jpg
   :alt: Inline image

   Inline image

Figure A. Raw histology image (r.tif), segmented histology (i.tif), and
scalebar (s.tif) of a rat cervical vagus nerve sample that served as
inputs to define the cross section of the nerve in the FEM.

.. figure:: uploads/e276681caea4240d2ef5d78de21ab87c/Picture3_Cuff1.jpg
   :alt: Inline image

   Inline image

Figure B. FEM of a rat cervical vagus nerve sample instrumented with a
bipolar cuff electrode.

The conductivity values applied to the rat cervical FEM are provided in
Table A, and the boundary conditions applied are provided in Table B.

Table A. Conductivity values for FEM of rat cervical vagus nerve. These
values were also used in multifascicular nerve model and human model
verifications.

.. raw:: html

   <table border="1" style="padding:5px">

.. raw:: html

   <thead>

.. raw:: html

   <tr class="header">

.. raw:: html

   <th>

Parameter

.. raw:: html

   </th>

.. raw:: html

   <th>

Application

.. raw:: html

   </th>

.. raw:: html

   <th>

Resistivity Ω-m

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   </thead>

.. raw:: html

   <tbody>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Endoneurium

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

Within each fascicle

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

.. raw:: html

   <p>

1.75 longitudinal

.. raw:: html

   </p>

.. raw:: html

   <p>

6 radial (rat and human)

.. raw:: html

   </p>

.. raw:: html

   <p>

12 radial (multifascicular dummy model)

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="even">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Saline

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

Cylindrical shell between the nerve and cuff

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

1/1.76

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Platinum

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

For both contacts

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

1/(9.43*106)

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="even">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Silicone

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

For electrode body

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

1012

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Muscle

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

Used for the surrounding “medium”: Everything outside of the nerve and
cuff, other than the saline layer between the nerve and cuff

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

.. raw:: html

   <p>

1/0.35 longitudinal

.. raw:: html

   </p>

.. raw:: html

   <p>

1/0.086 radial

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="even">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Epineurium

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

Within the nerve around each fascicle

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

6.3

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Encapsulation

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

Between cuff and nerve, and immediately surrounding cuff

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

6.3

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

Table B. Boundary conditions used in FEM of rat cervical vagus nerve,
multifascicular dummy nerve, and human cervical vagus nerve.

.. raw:: html

   <table border="1" style="padding:5px">

.. raw:: html

   <thead>

.. raw:: html

   <tr class="header">

.. raw:: html

   <th>

Parameter

.. raw:: html

   </th>

.. raw:: html

   <th>

Setting

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   </thead>

.. raw:: html

   <tbody>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Current conservation

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

All domains

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="even">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Initial condition

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

V=0 (all domains)

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Perineurium (sides of each fascicle)

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

.. raw:: html

   <p>

Modeled as contact impedance

.. raw:: html

   </p>

.. raw:: html

   <p>

1149 Ω-m \* 0.03 \* dfasc[m]

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="even">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Ground (all outer boundaries of the model)

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

V = 0

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr class="odd">

.. raw:: html

   <td align="center" style="vertical-align:middle">

Point current source (one in each contact)

.. raw:: html

   </td>

.. raw:: html

   <td align="center" style="vertical-align:middle">

.. raw:: html

   <p>

-1 mA

.. raw:: html

   </p>

.. raw:: html

   <ul>

.. raw:: html

   <p>

1 mA

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </ul>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

We compared thresholds for 100 5.7 µm myelinated axons (MRG model)
seeded in the cross section of the nerve in response to a single 100 µs
duration monophasic rectangular pulse. The differences in thresholds
between ASCENT and IT’IS model implementations was <4.2% for all fibers,
demonstrating strong agreement (Figure C).

.. figure:: uploads/3209b7b1f369a70a973385b635c801c9/Picture4.jpg
   :alt: Inline image

   Inline image

Figure C. Comparison of activation thresholds for the rat cervical vagus
nerve implementation in ASCENT and Sim4Life.

Multifascicular dummy nerve model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We validated activation thresholds for fibers seeded in a
multifascicular dummy nerve instrumented with a bipolar cuff electrode
(Figure D and E). The segmented histology was created using our
``mock_morphology_generator.py`` script (`S12
Text <S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology>`__).

.. figure:: uploads/2869942c6f0a8197e76ff97b8ad0133b/Picture5.jpg
   :alt: Inline image

   Inline image

Figure D. Mock morphology inputs to the define tissue boundaries for a
multifascicular dummy nerve for validation with Sim4Life. Scale bar is
100 µm long. The nerve is a perfect circle (diameter = 250 µm, centered
at (x,y)=(0,0) µm). The inners are also perfect circles: (1) diameter =
50 µm, centered at (x,y)=(40,50) µm, (2) diameter = 60 µm, centered at
(x,y)=(-50,0) µm, and (3) diameter = 80 µm, centered at (x,y)=(20,-60)
µm.

.. figure:: uploads/d4f2a7230a6f0faab591489c9348ed94/Picture6.jpg
   :alt: Inline image

   Inline image

Figure E. FEM of a multifascicular nerve sample instrumented with a
bipolar cuff electrode.

The conductivity values applied to multifascicular nerve sample finite
element model are provided in Table A, and the boundary conditions
applied are provided in Table B.

We seeded a single 5.7 µm diameter fiber in the center of each fascicle.
Between the ASCENT and IT’IS implementations, there was less than a 3%
difference in threshold to a single 100 µs duration monophasic
rectangular pulse.

Multifascicular human nerve model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We validated activation thresholds for fibers seeded in a
multifascicular human cervical vagus nerve instrumented with a LivaNova
bipolar cuff electrode (Figure F and G). The segmented histology was
created using Nikon NIS-Elements.

.. figure:: uploads/67640d7375fb580ad81d634bc6a35a3e/Picture7.jpg
   :alt: Inline image

   Inline image

Figure F. Raw histology image (r.tif), segmented inners (i.tif),
segmented nerve (n.tif), and scale bar (s.tif) of a human cervical vagus
nerve sample that served as inputs to define the cross section of the
nerve in the FEM for validation with Sim4Life.

.. figure:: uploads/df72ab32fc2b5f2b5376152462bdbeab/Picture8.jpg
   :alt: Inline image

   Inline image

Figure G. FEM of a human cervical vagus nerve sample instrumented with a
LivaNova cuff electrode.

The conductivity values applied to the human cervical vagus nerve sample
finite element model are provided in Table A, and the boundary
conditions applied are provided in Table B.

We seeded 5.7 µm diameter fibers in each fascicle. Between the ASCENT
and IT’IS implementations, there was less than 2.5% difference to a
single 100 µs duration monophasic rectangular pulse.

Comparison of MRG fit to Bucksot 2019
-------------------------------------

Comparison of MRG fit to Bucksot et al. 2019
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: uploads/f494c4342a397b94f92dacb2418b8e1e/Picture11.jpg
   :alt: Inline image

   Inline image

Figure A. Our piecewise polynomial fits to published MRG fiber
parameters compared to the Bucksot et al. 2019’s interpolation [1].
Single quadratic fits were used for all parameters except for internode
length, which has a linear fit below 5.643 µm (using MRG data at 2 and
5.7 µm) and a single quadratic fit at diameters greater than or equal to
5.643 µm (using MRG data >= 5.7 µm); 5.643 µm is the fiber diameter at
which the linear and quadratic fits intersected. The fiber diameter is
the diameter of the myelin. “Paranode 1” is the MYSA section, “paranode
2” is the FLUT section, and “internode” is the STIN section. The axon
diameter is the same for the node of Ranvier and MYSA (“node diameter”),
as well as for the FLUT and STIN (“axon diameter”). The node and MYSA
lengths are fixed at 1 and 3 μm, respectively, for all fiber diameters.

References
~~~~~~~~~~

1. Bucksot JE, Wells AJ, Rahebi KC, Sivaji V, Romero-Ortega M, Kilgard
   MP, et al. Flat electrode contacts for vagus nerve stimulation. PLoS
   One [Internet]. 2019;14(11):1–22. Available from:
   https://doi.org/10.1371/journal.pone.0215191
