
.. efficiencies

.. _ref_to_efficiencies:

Efficiencies
============


Efficiency is represented with the symbol :math:`\large{\eta}`.
Each :math:`\large{\eta}` will have a subscript to indicate the type of efficiency,
for example mixing efficiency can be shown as :math:`\large{\eta_{mix}}`

In a liquid propellant rocket engine there are two main, overall efficiencies to consider:

- Efficiency of the characteristic velocity, :math:`\large{\eta_{C^*}}`, called Cstar Efficiency
- Efficiency of the specific impulse, :math:`\large{\eta_{Isp}}`, called Isp Efficiency

Cstar Efficiency
----------------

The characteristic velocity, or Cstar (:math:`C^*`), is a property of propellant combustion 
products that will dictate
the flow rate (:math:`\dot m`) through a rocket thruster throat of given area (:math:`A_t`)
and discharge coefficient (:math:`C_d`). 
The ideal value of cstar is calculated by `RocketCEA <https://rocketcea.readthedocs.io/en/latest/>`_
a `python <http://www.python.org>`_ wrapper of the `NASA CEA FORTRAN Code <https://www.grc.nasa.gov/WWW/CEAWeb/ceaHome.htm>`_.


The Cstar Efficiency, :math:`\large{\eta_{C^*}}`, is used to calculate the delivered Cstar of the thruster.
Note that :math:`\large{\eta_{C^*}}` is calculated from the product of other chamber efficiencies.

.. math:: 
    
    \Large{C^*_{del} = C^*_{ODE} \cdot \eta_{C^*}}


Thruster mass flow rate is then given by the following equation.

.. math:: 

    \Large{\dot m = \frac {P_c \cdot A_t \cdot C_d}  {C^*_{del}} }

Note that as :math:`\large{C^*_{del}}` gets smaller :math:`\large{\dot m}` gets larger.
Thus when Cstar Efficiency, :math:`\large{\eta_{C^*}}` gets smaller,  :math:`\large{\dot m}` gets larger.

:math:`\large{C^*_{del}}`  and  :math:`\large{\dot m}` are **inversely** proportional.

The Cstar Efficiency, :math:`\large{\eta_{C^*}}`, is often used to characterize injector design quality
since fully mixed, vaporized and combusted propellants tend to have higher :math:`\large{\eta_{C^*}}`.

Discharge Coefficient
---------------------

When calculating throat discharge coefficient (:math:`C_d`) with a model using constant gas properties and ignoring the boundary layer,
:math:`C_d` is shown to be primarily a function of the upstream radius
of curvature, :ref:`RupThroat <ref_to_geom_image>`.
The ratio of specific heats of the combustion gas, gamma (:math:`\large{\gamma}`) has a small influence
at low values of :ref:`RupThroat <ref_to_geom_image>`, but in this simple model :math:`\large{\gamma}` can be ignored
with little difference in calculated :math:`C_d`.

The chart at below shows :math:`C_d` as calculated by such a model having constant gas properties
and ignoring the boundary layer.
The chart compares those calculations with published values from 
`NASA SP 8120 <https://ntrs.nasa.gov/search.jsp?R=19770009165>`_ and  from
`NASA Technical Memorandum 33-548, Simplified Procedures for Correlation of Experimentally Measured and Predicted Thrust
Chamber Performance <https://ntrs.nasa.gov/citations/19730012958>`_

More sophisticated models will, in general, predict :math:`C_d` values
lower than what is shown here, however, this more simple model shows good agreement with both NASA sources.
(The NASA curves were digitized using `Digiplot <https://digiplot.readthedocs.io/en/latest/>`_.)

.. image:: ./_static/cmp_nasa_cd.png
    :width: 55%


.. raw:: html

    <table width="100%">
    <tr>
    <th style="text-align:center;"> NASA SP 8120 </th>
    <th style="text-align:center;"> NASA 33-548 </th>
    </tr>
    <tr>
    <td width="40%">
    <a class="reference internal image-reference" href="./_static/At_flow_vs_geom_v2.jpg">
    <img src="./_static/At_flow_vs_geom_v2.jpg">
    </a>
    </td>
    <td>
    <a class="reference internal image-reference" href="./_static/Cd_NASA_1973.jpg">
    <img src="./_static/Cd_NASA_1973.jpg" ; width="60%">
    </a>
    </td>
    </tr>
    <tr>
    <td colspan="2" style="text-align:center;">
    <p><cite>Click image to see full size</cite></p>
    </td>
    </tr>
    </table>



Shown above-left is Figure 3 from `NASA SP 8120 <https://ntrs.nasa.gov/search.jsp?R=19770009165>`_,
above-right, is figure 9 from 1973 `NASA Technical Memorandum 33-548, Simplified Procedures for Correlation of Experimentally Measured and Predicted Thrust
Chamber Performance <https://ntrs.nasa.gov/citations/19730012958>`_.

Figure 3 from NASA SP 8120 as well as the top curve of the NASA 33-548 figure by Kliegel and Levine
show very similar predictions to the constant gas properties calculations.

While :ref:`RupThroat <ref_to_geom_image>` is clearly a major independent parameter for calculating :math:`C_d`, 
the wide spread of :math:`C_d` values in the `NASA 33-548 report <https://ntrs.nasa.gov/citations/19730012958>`_ 
would seem to indicate that additional influencing parameters should, perhaps be considered.

:math:`C_d` Monte Carlo
~~~~~~~~~~~~~~~~~~~~~~~

In order to characterize the variation in :math:`C_d` beyond just :ref:`RupThroat <ref_to_geom_image>` 
and to identify additional influencing parameters, a
`Monte Carlo <https://en.wikipedia.org/wiki/Monte_Carlo_method>`_ analysis was conducted
on a wide range of propellant combinations, chamber pressures and thrust chamber geometries. Many thousands of boundary layer
analyses were performed such that the calculated :math:`C_d` included boundary layer influences.
:math:`C_d` was then fitted with a :ref:`Multi-layer Perceptron regressor <ref_to_mlp_summary>`.

The independent parameters in the `Monte Carlo <https://en.wikipedia.org/wiki/Monte_Carlo_method>`_ analysis 
are shown across the x axis of the chart below. The y axis shows the correlation coefficient that results from 
fitting :math:`C_d` with a :ref:`Multi-layer Perceptron regressor <ref_to_mlp_summary>`
when selecting, one by one, the best scoring independent parameter to add next.

The chart shows that the :math:`C_d` is well characterized by using three independent parameters, throat radius (Rthrt), 
chamber pressure (Pc) and upstream radius of curvature (RupThroat).

.. image:: ./_static/cd_corr_params.png
    :width: 70%

Using the above dependence sensitivities, a correlation of :math:`C_d` was created from the 
`Monte Carlo <https://en.wikipedia.org/wiki/Monte_Carlo_method>`_ data using
a :ref:`Multi-layer Perceptron regressor <ref_to_mlp_summary>`
that includes the effects of a boundary layer analysis.

The plots below show the sensitivity of the :math:`C_d`
correlation to the three independent parameters, throat radius (Rthrt), 
chamber pressure (Pc) and upstream radius of curvature (RupThroat).

The simple, constant gas properties model is shown for comparison.

Note that the :ref:`Multi-layer Perceptron regressor <ref_to_mlp_summary>`
tends to be a bit piece-wise linear and, compared to the simple model, predicts lower :math:`C_d`.
The decrement to :math:`C_d` is in the range of 0.002 to 0.013 depending on the thruster design.


.. raw:: html

    <table width="100%">
    <tr>
    <th style="text-align:center;"> Throat Radius=1 inch </th>
    <th style="text-align:center;"> Chamber Pressure=200 psia </th>
    </tr>
    <tr>
    <td width="50%">
    <a class="reference internal image-reference" href="./_static/cmp_cd_calcs_pc.png">
    <img src="./_static/cmp_cd_calcs_pc.png">
    </a>
    </td>
    <td>
    <a class="reference internal image-reference" href="./_static/cmp_cd_calcs_rthrt.png">
    <img src="./_static/cmp_cd_calcs_rthrt.png" >
    </a>
    </td>
    </tr>
    <tr>
    <td colspan="2" style="text-align:center;">
    <p><cite>Click image to see full size</cite></p>
    </td>
    </tr>
    </table>


.. raw:: html

    <table width="100%">
    <tr>
    <th style="text-align:center;"> High Pc, Large Throat </th>
    <th style="text-align:center;"> Low Pc, Small Throat </th>
    </tr>
    <tr>
    <td width="50%">
    <a class="reference internal image-reference" href="./_static/cmp_cd_calcs_best.png">
    <img src="./_static/cmp_cd_calcs_best.png">
    </a>
    </td>
    <td>
    <a class="reference internal image-reference" href="./_static/cmp_cd_calcs_worst.png">
    <img src="./_static/cmp_cd_calcs_worst.png" >
    </a>
    </td>
    </tr>
    <tr>
    <td colspan="2" style="text-align:center;">
    <p><cite>Click image to see full size</cite></p>
    </td>
    </tr>
    </table>


Isp Efficiency
--------------

Vacuum specific impulse (:math:`\large{Isp_{vac}}`) is defined as steady state vacuum thrust 
(:math:`\large{F_{vac}}`) 
divided by steady state mass flow rate (:math:`\large{\dot m}`).

.. math::

    \Large{Isp_{vac} = F_{vac} / \dot m}

The maximum possible achievable :math:`Isp_{vac}` is the one dimensional equilibrium (ODE) value
predicted by the `NASA CEA FORTRAN Code <https://www.grc.nasa.gov/WWW/CEAWeb/ceaHome.htm>`_
via `RocketCEA <https://rocketcea.readthedocs.io/en/latest/>`_ .

The delivered Isp (:math:`Isp_{del}`) of a real thrust chamber will equal the ideal ODE performance 
(:math:`\large{Isp_{ODE}}`)
decremented by various efficiencies.

Thrust chamber performance efficiencies are usually broken down into two categories, 
the combustion chamber and the nozzle. The combustion chamber is where propellants must get
mixed, vaporized and combusted efficiently. The nozzle is where the combustion products must
be expanded and directed aft efficiently. The Greek letter, :math:`\large{\eta}`, is often used to
represent each of the efficiencies.

These efficiencies can have different names, 
depending on the aerospace company or government agency,
however, common designations are:

.. code-block:: text

    _________Combustion Chamber Losses_________
    - Mixing Loss - How well does the injector mix the oxidizer and fuel
    - Vaporization Loss - Both propellants must vaporize before they can combust
    - Heat Loss - The chamber wall may lose heat to the environment
                  (note that regen-cooled chambers recover the lost heat)
                  (and that ablative chambers lose heat to phase change of the ablative)
    - Fuel Film Cooling Loss - A barrier of lower temperature fuel rich combustion gas 
                               along the wall may be used to limit wall material temperature
    - Pulsing Loss - When short pulses of thrust are used, the performance is 
                     degraded from the steady state performance
    
    _______________Nozzle Losses_______________
    - Divergence Loss - nonaxial directed flow at nozzle exit.
    - Two Phase Loss - drag from solid or liquid particles in flow stream 
                       (e.g. condensibles, uncombusted, aluminized or gel propellants)
    - Kinetic Loss - finite reaction rates in the nozzle 
                     (i.e. ranging from frozen to equilibrium chemistry)
    - Boundary Layer Loss - viscous drag along the nozzle contour 
                           (often combined with nozzle heat loss)
        ... Heat Loss - Included in boundary layer loss, the nozzle wall may lose heat 
                        to the environment
                        (note that regen-cooled nozzles recover the lost heat)

Delivered steady state Isp (:math:`Isp_{del}SS`) for the thrust chamber can be calculated from the
one dimensional equilibrium Isp (:math:`Isp_{ODE}`)
that is modified by the above efficiencies.

.. _ref_to_full_efficiency_eqn:

.. math::
    \Large{Isp_{del}SS = Isp_{ODE} * \eta_{ML} * \eta_{Vap} * \eta_{HL} * \eta_{FFC} * \eta_{Div} * \eta_{TP} * \eta_{Kin} * \eta_{BL}}
    
If thruster on/off pulsing is involved, then the steady state Isp equation may be further modified as shown below.
Note also that pulsing usually changes the overall thruster mixture ratio due to different leads or lags of the
fuel and oxidizer being fed into the thruster, as well as any dribble volume differences between fuel and oxidizer.

.. math:: 
    \Large{Isp_{del} = Isp_{del}SS * \eta_{Pulse}}

In python code the equation might look like:

.. code-block:: python

    IspDelSS = IspODE * effML * effVap * effHL * effFFC * effDiv * effTP * effKin  * effBL

    #... or in alternate form:
    IspDelSS = IspODE * [ effML * effVap * effHL * effFFC * effDiv * effTP * effKin - (1 - effBL) ]
    
    # if Pulsing
    IspDel = IspDelSS * effPulse
    
    """
    where:
    IspDelSS = Steady State Delivered Isp (sec)
    IspDel   = Delivered Isp (sec)
    IspODE   = One Dimensional Equilibrium Isp (directly from RocketCEA)
    effML    = Mixing Efficiency
    effVap   = Vaporization Efficiency
    effHL    = Chamber Heat Loss Efficiency
    effDiv   = Nozzle Divergence Efficiency
    effTP    = Nozzle Two-Phase Efficiency
    effKin   = Nozzle Kinetic Efficiency
    effBL    = Nozzle Boundary Layer Efficiency (includes nozzle heat loss)
    effFFC   = Fuel Film Cooling Efficiency of Chamber
    effPulse = Pulsing Efficiency of Thruster
    """
 
.. note::
    
    Note that the nozzle boundary layer loss is often calculated as a
    force subtraction from the thrust chamber as shown in the alternate equation above. 
    The boundary layer removes an annular ring
    of flow area from the exit plane of the nozzle, and becomes a subtractive loss
    to thrust.

    It is possible for either of the two equations to be correct, depending on the manner in which
    the nozzle boundary layer loss correlation was formulated. In other words effBL
    can be tailored to either equation format. In a preliminary design analysis, 
    the uncertainty in the boundary layer loss may well render the issue moot since both 
    equations yield very nearly the same answer and the difference is likely below the ability
    of an engine test to measure.

    "Although both approaches have their ardent supporters, there are really no
    significant differences between the two."
    -- `D.E. Coats <https://arc.aiaa.org/doi/book/10.2514/4.866760>`_

The image below from 
`NASA CR-179025 pub:1986 <https://ntrs.nasa.gov/search.jsp?R=19870009172>`_
illustrates the various mechanisms, where they occur and their major influencing effects.

.. image:: ./_static/eff_zones.jpg
    :width: 80%


Perfect Injector
----------------

When approaching the performance analysis of a liquid bi-propellant thrust chamber it is useful to 
realize that a number of the above losses are almost completely out of the designers control.  
The nozzle losses, in particular, are fixed once a few basic 
thrust chamber design choices are made. 

The boundary layer, divergence and
kinetic losses are fixed once the engine's thrust, chamber pressure, 
propellant combination, nozzle contour and area ratio are selected.

Therefor, a powerful approach to preliminary design is to start with an engine that has a 
**perfect injector**. In other words, the chamber's mixing, vaporization and 
heat losses are *temporarily* ignored while the nozzle losses are evaluated.

This approach is further supported by the fact that in production engines,
98% efficiency is a very typical value for all the combined chamber losses.
Using a constant 98% for effERE (:math:`\large{\eta_{ERE}}`) and calculating the nozzle losses will be a good
first approximation for most liquid thrust chambers.

.. note::

    When optimizing thruster mixture ratio, a perfect injector can be a bad assumption.
    
    The  injector's ability to mix the propellants via :math:`E_m` can affect
    :math:`MR_{opt}`, (:ref:`see Em impact on MRopt <ref_to_EmMRopt>`)

