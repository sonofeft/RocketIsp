
.. models

Models
======


In **RocketIsp** there are 5 objects that work together to model a liquid propellant rocket thruster::

    1) Geometry       - Holds all the major thrust chamber geometry values
    2) Efficiencies   - Holds all of the thrust chamber efficiencies
    3) CoreStream     - Models combustion gas stream tubes (both core and barrier)
    4) Injector       - Models injector physical features and calculates injector efficiencies
    5) RocketThruster - Models the overall thruster Isp, thrust, mixture ratio, etc.

.. note::

    The Injector object is often omitted from an analysis when the details of the injector are not known.
    Simply assuming an injector efficiency of 98 or 99 percent is usually representative of a modern injector.

Geometry
--------

The Geometry object holds all the major thrust chamber geometry values.
The code snippet below shows how to create a Geometry object, and the definition of all the 
parameters.

See the diagram below the parameter definitions for the physical location of the parameters on the thruster.

.. note::

    Note that most of the parameters are dimensionless, such that if the throat radius (Rthrt) is changed,
    the rest of the geometry will scale appropriately.

.. code-block:: python

    from rocketisp.geometry import Geometry
    G = Geometry( Rthrt=1, CR=2.5, eps=20,  pcentBell=80, LnozInp=None,
                  RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                  LchmOvrDt=3.0, LchmMin=1.0, LchamberInp=None)

.. raw:: html

    <dl class="field-list simple">
    <dt class="field-odd">Parameters</dt>
    <dd class="field-odd"><ul class="simple">
    <li><p><strong>Rthrt</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- in, throat radius</p></li>
    <li><p><strong>CR</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- chamber contraction ratio (Ainj / Athroat)</p></li>
    <li><p><strong>eps</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- nozzle area ratio (Aexit / Athroat)</p></li>
    <li><p><strong>pcentBell</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- nozzle percent bell (Lnoz / L_15deg_cone)</p></li>
    <li><p><strong>LnozInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- in, user input nozzle length (will override pcentBell)</p></li>
    <li><p><strong>RupThroat</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- radius of curvature just upstream of throat (Rupstream / Rthrt)</p></li>
    <li><p><strong>RdwnThroat</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- radius of curvature just downstream of throat (Rdownstream / Rthrt)</p></li>
    <li><p><strong>RchmConv</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- radius of curvature at start of convergent section (Rconv / Rthrt)</p></li>
    <li><p><strong>cham_conv_deg</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- deg, half angle of conical convergent section</p></li>
    <li><p><strong>LchmOvrDt</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- ratio of chamber length to throat diameter (Lcham / Dthrt)</p></li>
    <li><p><strong>LchmMin</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- in, minimum chamber length (will override LchmOvrDt)</p></li>
    <li><p><strong>LchamberInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- in, user input value of chamber length (will override all other entries)</p></li>
    </ul>
    </dd>
    </dl>

.. _ref_to_geom_image:

.. image:: ./_static/chamber_geometry.jpg
    :width: 69%

The Geometry object can be used in a stand-alone manner to generate a thruster inner profile.
The following script will create the image shown below.

.. code-block:: python

    from rocketisp.geometry import Geometry

    # SSME Geometry
    G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5, LnozInp=121,
                 RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
                 LchmOvrDt=2.4842/2)

    G.plot_geometry( title='SSME Profile', png_name='ssme_geom.png', show_grid=True)

.. image:: ./_static/ssme_geom.png

Efficiencies
------------

The various efficiencies that apply to a liquid propellant thruster are discussed at :ref:`JANNAF Standard <ref_to_jannaf_standard>`
and :ref:`Efficiencies <ref_to_efficiencies>`.

The Efficiencies object collects and coordinates the individual efficiencies. 

It does not calculate any individual efficiencies, however, it does combine all nozzle efficiencies
into an overall nozzle efficiency; all chamber efficiencies into an overall chamber efficiency; and
it combines the nozzle and chamber efficiencies into an overall Isp efficiency.

If the engine pulses, it also creates an overall pulsing efficiency.

.. note::

    Unless specified otherwise, all efficiencies are set to 1.0

The most simple usage is shown in the python scripts below.
    
If the user would like to set the nozzle and chamber efficiencies to a constant, 
the following script can be employed.


.. code-block:: python

    from rocketisp.efficiencies import Efficiencies

    E = Efficiencies( ERE=0.98, Noz=0.97 )
    E.summ_print()

    #       creates the following output
    ============ Thruster Efficiencies ============
                  0.95060 Overall Isp Efficiency
    ------------  0.97000 (constant) Nozzle Efficiency ------------
    ------------  0.98000 (constant) Energy Release Efficiency ------------

Or perhaps simply set an overall Isp efficiency.


.. code-block:: python

    from rocketisp.efficiencies import Efficiencies

    E = Efficiencies( Isp=0.95 )
    E.summ_print()

    #       creates the following output
    ============ Thruster Efficiencies ============
                  0.95000 Overall Isp Efficiency

In a more complete analysis, where both the nozzle and injector are fully analyzed, the following
output is typical.

.. code-block:: python

    ============ Thruster Efficiencies ============
                  0.92196 Overall Isp Efficiency
    ------------  0.94642 Nozzle Efficiency ------------
            Div = 0.98547 (simple fit eps=35, %bell=70) Divergence Efficiency of Nozzle
            Kin = 0.96641 (MLP fit) Kinetic Efficiency of Nozzle
             BL = 0.99376 (MLP fit) Boundary Layer Efficiency of Nozzle
             TP = 1.00000 (default) Two Phase Efficiency of Nozzle
    ------------  0.97415 Energy Release Efficiency ------------
            Mix = 0.99987 (mixAngle=0.23 deg) Inter-Element Mixing Efficiency of Injector
             Em = 0.98611 (Rupe Em=0.8) Intra-Element Mixing Efficiency of Injector
            Vap = 0.98801 (gen vaporized length) Vaporization Efficiency of Injector
             HL = 1.00000 (default) Heat Loss Efficiency of Chamber
            FFC = 1.00000 (default) Fuel Film Cooling Efficiency of Chamber


CoreStream
----------

The CoreStream object assumes that all efficiencies have been set, either by the user
or computed by an efficiency model.  It uses those efficiencies along with the Geometry object
to calculate overall thrust, Isp and flow rates.

A CoreStream object is created as shown below

.. code-block:: python

    C = CoreStream( geomObj=geomObj, effObj=effObj, 
                    oxName='N2O4', fuelName='MMH',  MRcore=1.9,
                    Pc=500, CdThroat=0.995, Pamb=0.0, adjCstarODE=1.0, adjIspIdeal=1.0,
                    pcentFFC=0.0, ko=0.035, i

The parameters in the CoreStream object are defined as...

.. raw:: html

    <dl class="field-list simple">
    <dt class="field-odd">Parameters</dt>
    <dd class="field-odd"><ul class="simple">
    <li><p><strong>geomObj</strong> (<a class="reference internal" href="#geometry" title="rocketisp.geometry.Geometry"><em>Geometry</em></a>) -- Geometry that describes thruster</p></li>
    <li><p><strong>effObj</strong> (<a class="reference internal" href="#efficiencies" title="rocketisp.efficiencies.Efficiencies"><em>Efficiencies</em></a>) -- Efficiencies object to hold individual efficiencies</p></li>
    <li><p><strong>oxName</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.8)"><em>str</em></a>) -- name of oxidizer (e.g. N2O4, LOX)</p></li>
    <li><p><strong>fuelName</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.8)"><em>str</em></a>) -- name of fuel (e.g. MMH, LH2)</p></li>
    <li><p><strong>MRcore</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- mixture ratio of core flow (ox flow rate / fuel flow rate)</p></li>
    <li><p><strong>Pc</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- psia, chamber pressure</p></li>
    <li><p><strong>CdThroat</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- Cd of throat (RocketThruster object may override if calc_CdThroat is True)</p></li>
    <li><p><strong>Pamb</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- psia, ambient pressure (for example sea level is 14.7 psia)</p></li>
    <li><p><strong>adjCstarODE</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- multiplier on NASA CEA code value of cstar ODE (default is 1.0)</p></li>
    <li><p><strong>adjIspIdeal</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- multiplier on NASA CEA code value of Isp ODE (default is 1.0)</p></li>
    <li><p><strong>pcentFFC</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- percent fuel film cooling (if &gt; 0 then add BarrierStream)</p></li>
    <li><p><strong>ko</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- entrainment constant (passed to BarrierStream object, range from 0.03 to 0.06)</p></li>
    <li><p><strong>ignore_noz_sep</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#bool" title="(in Python v3.8)"><em>bool</em></a>) -- flag to force nozzle flow separation to be ignored (USE WITH CAUTION)</p></li>
    </ul>
    </dd>
    </dl>
    
.. note::

    A CoreStream object is seldom used on its own. It is most useful when controlled by a RocketThruster object.

Some simple delivered Isp calculations can be performed with an isolated CoreStream object as shown in the following code,
however, a CoreStream object is much more useful when controlled by a RocketThruster object.

In this simple, isolated CoreStream approach, the efficiencies of the chamber and nozzle 
are fixed values (ERE=0.98, Noz=0.97).

.. code-block:: python

    from rocketisp.geometry import Geometry
    from rocketisp.efficiencies import Efficiencies
    from rocketisp.stream_tubes import CoreStream

    C = CoreStream( geomObj=Geometry(eps=35), 
                    effObj=Efficiencies(ERE=0.98, Noz=0.97), 
                    oxName='LOX', fuelName='CH4',  MRcore=3.6,
                    Pc=500, Pamb=14.7)

    for name in ['IspODE','IspDel','IspODF']:
        print( '%8s ='%name, '%.1f'%C(name) )
    print('%8s ='%'IspAmb','%.1f'%C('IspAmb'), C('noz_mode'))

    # ----------- outputs ------------
      IspODE = 363.2
      IspDel = 345.3
      IspODF = 334.2
      IspAmb = 325.1 Separated (Psep=4.84056, epsSep=14.4921)

Notice in the above example that the nozzle will have separated flow at sea level.
**RocketIsp** expects the nozzle to separate at any area ratio above 14.5:1.

BarrierStream
-------------

.. code-block:: python

    class BarrierStream:
        def __init__(self, coreObj, pcentFFC=10.0, ko=0.035):

If fuel film cooling (FFC) has been specified with the **CoreStream** pcentFFC input, then a **BarrierStream**
object is created automatically in order to calculate overall thruster mixture ratio, Isp and wall gas temperature.
Engines that use ablative or radiation cooled chambers use FFC in order to achieve longer hardware lifetimes
(although in some uncommon situations, short hardware lifetimes might be appropriate).

The mixture ratio of the barrier will be calculated as a mixture of the entrained core flow with the fuel film cooling flow.
(In the MRbarrier equation below, wdot is flow rate.)

The engine delivered Isp will be the mass-averaged Isp values of the core and barrier flow rates.

.. image:: ./_static/entrained_ffc.jpg

The overall thruster MR will be less than MRcore... MRthruster = MRcore * (1 - %FFC/100) 

The calculation of entrained core gases, comes from `Combustion effects on film cooling, NASA-CR-135052 <https://ntrs.nasa.gov/citations/19770014416>`_.
That model assumes two stream tubes, as shown in the illustration above, and uses the input, ko (typical range from 0.03 to 0.06)
as the main input affecting entrainment.

As a general first estimate of ko, the default value of 0.035 is a good starting point.
Note that `Combustion effects on film cooling, NASA-CR-135052 <https://ntrs.nasa.gov/citations/19770014416>`_
recommends using test data to determine the best value.

.. _ref_to_RocketThruster:

RocketThruster
--------------

The RocketIsp object coordinates the Geometry, Efficiencies, CoreStream and Injector objects.

It does so in order to
calculate delivered Isp for liquid rocket thrust chambers by the :ref:`simplified JANNAF Standard <ref_to_jannaf_standard>` method.

A RocketThruster object is created as shown below. 
Note that a **CoreStream** object and, optionally, an **Injector** object are part of the input.

.. code-block:: python

    R = RocketThruster(name='Rocket Thruster',
                       coreObj=CoreStream(), injObj=None, noz_regen_eps=1.0, 
                       pulse_sec=float('inf'), pulse_quality=0.8,
                       isRegenCham=0, calc_CdThroat=True)

.. raw:: html

    <dl class="py class">
    <dt id="rocketisp.rocket_isp.RocketThruster">
    <dl class="field-list simple">
    <dt class="field-odd">Parameters</dt>
    <dd class="field-odd"><ul class="simple">
    <li><p><strong>coreObj</strong> (<a class="reference internal" href="#corestream" title="rocketisp.stream_tubes.CoreStream"><em>CoreStream</em></a>) -- CoreStream object</p></li>
    <li><p><strong>injObj</strong> (<a class="reference internal" href="#injector" title="rocketisp.injector.Injector"><em>Injector</em></a>) -- Injector object (optional)</p></li>
    <li><p><strong>noz_regen_eps</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- regen cooled nozzle area ratio</p></li>
    <li><p><strong>pulse_sec</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- duration of pulsing engine (default = infinity)</p></li>
    <li><p><strong>pulse_quality</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- on a scale of 0.0 to 1.0, how good is engine at pulsing</p></li>
    <li><p><strong>isRegenCham</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#bool" title="(in Python v3.8)"><em>bool</em></a>) -- flag to indicate chamber is regen cooled</p></li>
    <li><p><strong>calc_CdThroat</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#bool" title="(in Python v3.8)"><em>bool</em></a>) -- flag to trigger calc_CdThroat</p></li>
    </ul>
    </dd>
    </dl>


A typical usage might look something like the following.

To rough out a 6000 lbf LOX/LH2 space engine. Let **RocketThruster** calculate the nozzle losses, but input
a constant 99% for the chamber efficiency.  

Use the method **scale_Rt_to_Thrust** in order to scale the geometry to give 6000 lbf
of vacuum thrust (i.e. Pamb=0.0).


.. literalinclude:: ./_static/example_scripts/thruster_only.py


The resulting summary print is:

.. literalinclude:: ./_static/example_scripts/thruster_only.out

.. _ref_to_Injector:

Injector
--------

The Injector object is more complex than the other 4 main objects (Geometry, Efficiencies, CoreStream and RocketThruster).
Choices made for the Injector affect feed system pressures and pressure drops, chamber acoustics, combustion stability, size and type of 
injector elements, injection velocities and the combustor efficiencies for vaporization and propellant mixing within an element as well as
between elements.

Note that the Injector object uses the companion project 
`RocketProps <https://rocketprops.readthedocs.io/en/latest/>`_ 
to calculate oxidizer and fuel fluid properties based on the inlet propellant temperatures(**Tox** and **Tfuel**) as well as the
pressure taken from the CoreStream object.

.. raw:: html

    <dl class="field-list simple">
    <dt class="field-odd">Parameters</dt>
    <dd class="field-odd"><ul class="simple">
    <li><p><strong>coreObj</strong> (<a class="reference internal" href="#corestream" title="rocketisp.stream_tubes.CoreStream"><em>CoreStream</em></a>) -- CoreStream object</p></li>
    <li><p><strong>Tox</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- degR, temperature of oxidizer</p></li>
    <li><p><strong>Tfuel</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- degR, temperature of fuel</p></li>
    <li><p><strong>Em</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- intra-element Rupe mixing factor</p></li>
    <li><p><strong>fdPinjOx</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- fraction of Pc used as oxidizer injector pressure drop</p></li>
    <li><p><strong>fdPinjFuel</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- fraction of Pc used as fuel injector pressure drop</p></li>
    <li><p><strong>dpOxInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/constants.html#None" title="(in Python v3.8)"><em>None</em></a><em> or </em><a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- input value of injector pressure drop for oxidizer  (overrides fdPinjOx)</p></li>
    <li><p><strong>dpFuelInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/constants.html#None" title="(in Python v3.8)"><em>None</em></a><em> or </em><a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- input value of injector pressure drop for fuel  (overrides fdPinjFuel)</p></li>
    <li><p><strong>setNelementsBy</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.8)"><em>str</em></a>) -- flag determines how to calculate number of elements ( &quot;acoustics&quot;, &quot;elem_density&quot;, &quot;input&quot;)</p></li>
    <li><p><strong>elemDensInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- elem/in**2, input value for element density (setNelementsBy == &quot;elem_density&quot;)</p></li>
    <li><p><strong>NelementsInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- input value for number of elements (setNelementsBy == &quot;input&quot;)</p></li>
    <li><p><strong>OxOrfPerEl</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- number of oxidizer orifices per element</p></li>
    <li><p><strong>FuelOrfPerEl</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- number of fuel orifices per element</p></li>
    <li><p><strong>lolFuelElem</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#bool" title="(in Python v3.8)"><em>bool</em></a>) -- flag for like-on-like fuel element (determines strouhal multiplier)</p></li>
    <li><p><strong>setAcousticFreqBy</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.8)"><em>str</em></a>) -- flag indicating how to determnine design frequency. (can be &quot;mode&quot; or &quot;freq&quot;)</p></li>
    <li><p><strong>desAcousMode</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.8)"><em>str</em></a><em> or </em><a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- driving acoustic mode of injector OR acoustic mode multiplier (setNelementsBy==&quot;acoustics&quot; and setAcousticFreqBy==&quot;mode&quot;)</p></li>
    <li><p><strong>desFreqInp</strong> (<a class="reference external" href="https://docs.python.org/3/library/constants.html#None" title="(in Python v3.8)"><em>None</em></a><em> or </em><a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- Hz, driving acoustic frequency of injector (sets D/V if setNelementsBy==&quot;acoustics&quot; and setAcousticFreqBy==&quot;freq&quot;)</p></li>
    <li><p><strong>CdOxOrf</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- flow coefficient of oxidizer orifices</p></li>
    <li><p><strong>CdFuelOrf</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- flow coefficient of fuel orifices</p></li>
    <li><p><strong>dropCorrOx</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- oxidizer drop size multiplier</p></li>
    <li><p><strong>dropCorrFuel</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- fuel drop size multiplier</p></li>
    <li><p><strong>pcentFFC</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- percent fuel film cooling ( FFC flowrate / total fuel flowrate)</p></li>
    <li><p><strong>DorfMin</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- in, minimum orifice diameter (lower limit)</p></li>
    <li><p><strong>LfanOvDorfOx</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- fan length / oxidizer orifice diameter</p></li>
    <li><p><strong>LfanOvDorfFuel</strong> (<a class="reference external" href="https://docs.python.org/3/library/functions.html#float" title="(in Python v3.8)"><em>float</em></a>) -- fan length / fuel orifice diameter</p></li>
    </ul>
    </dd>
    </dl>

