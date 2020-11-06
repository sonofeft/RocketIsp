import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, CWheel
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA


# the following lists are used by eff_bl_NASA
# eps = 3
pxd3L = [7.91256, 9.98901, 13.0916, 18.3392, 25.2661, 34.5208, 49.9948, 72.4052, 99.339, 140.906, 192.518, 251.267, 339.044, 453.694, 654.568, 1013.25, 1939.3]
pct3L = [1.29734, 1.17043, 1.03445, 0.907531, 0.798746, 0.717158, 0.635569, 0.572111, 0.526784, 0.481457, 0.43613, 0.408934, 0.390803, 0.363607, 0.345476, 0.33641, 0.327345]

# eps = 5
pxd5L = [8.04822, 9.98009, 13.3161, 18.3457, 24.3662, 35.6278, 53.5449, 74.1077, 98.4277, 145.243, 206.618, 289.919, 435.719, 625.541, 1016.2, 1937.68]
pct5L = [1.99111, 1.79167, 1.59223, 1.42271, 1.27313, 1.09364, 0.954028, 0.86428, 0.784505, 0.704729, 0.644897, 0.614981, 0.575094, 0.55515, 0.515262, 0.50529]

# eps = 10
pxd10L = [7.7234, 10.0259, 13.6869, 18.6847, 25.5075, 34.3467, 49.5362, 71.7708, 99.3329, 147.251, 221.303, 331.076, 493.039, 698.179, 1016.2, 1928.84]
pct10L = [3.00825, 2.71906, 2.42988, 2.19055, 1.98114, 1.82159, 1.64209, 1.48254, 1.37285, 1.25319, 1.16344, 1.10361, 1.04378, 0.983944, 0.944056, 0.91414]

# eps = 20
pxd20L = [7.93846, 9.98009, 13.1345, 17.4448, 23.4901, 32.9605, 46.6744, 66.7022, 99.3329, 146.579, 219.286, 322.107, 484.094, 730.881, 1020.86, 1937.68]
pct20L = [4.12511, 3.80601, 3.45699, 3.12791, 2.8487, 2.58943, 2.33016, 2.12075, 1.89139, 1.72187, 1.59223, 1.48254, 1.38282, 1.32299, 1.23324, 1.14349]

# eps = 40
pxd40L = [8.01147, 9.98009, 12.7786, 15.9917, 20.6643, 27.0714, 36.2861, 47.5369, 64.8952, 81.9594, 99.3329, 130.729, 179.284, 244.75, 337.194, 460.322, 619.84, 779.252, 1011.56, 1387.27, 1946.57]
pct40L = [5.17216, 4.70348, 4.28466, 3.96556, 3.62651, 3.31738, 3.05811, 2.82875, 2.62932, 2.47974, 2.37004, 2.23044, 2.09083, 1.98114, 1.87145, 1.80164, 1.72187, 1.68198, 1.63212, 1.58226, 1.51246]

# eps = 60
pxd60L = [8.08515, 9.93451, 12.7203, 16.5124, 21.2397, 27.6982, 36.2861, 49.0848, 66.7022, 99.3329, 145.243, 206.618, 296.631, 406.805, 578.709, 779.252, 1011.56, 1362.1, 1946.57]
pct60L = [6.02975, 5.5511, 5.04253, 4.60376, 4.22483, 3.90573, 3.60657, 3.32735, 3.07805, 2.79884, 2.56948, 2.38002, 2.23044, 2.11077, 2.00108, 1.91134, 1.84153, 1.77173, 1.69195]

# eps = 80
pxd80L = [8.04822, 9.93451, 12.7203, 16.8175, 23.0639, 31.9211, 46.0379, 66.0944, 100.247, 146.579, 211.401, 313.381, 449.906, 651.849, 861.813, 1011.56, 1349.69, 1928.84]
pct80L = [7.14661, 6.37877, 5.72062, 5.15222, 4.62371, 4.18494, 3.78606, 3.44702, 3.11794, 2.85867, 2.64926, 2.45979, 2.2803, 2.14069, 2.04097, 1.99111, 1.91134, 1.81162]

pxdLL = [pxd3L, pxd5L, pxd10L, pxd20L, pxd40L, pxd60L, pxd80L]
pctLL = [pct3L, pct5L, pct10L, pct20L, pct40L, pct60L, pct80L]

MARKERL = ['o','v','^','<','>','d','X','P','s','p','*','.']
COLORL = ['g','c','b','y','#FFA500','m','r']
    
nasa_epsL = [3., 5., 10., 20., 40., 60., 80.]


F = Figure( figsize=(6,5), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title=' NASA SP 8120\n Boundary Layer Efficiency', show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'nasa_sp8120_bl_eff.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

curveL = []

# plot data points
i = 0
for area_ratio, pxdL, lossL in zip(nasa_epsL, pxdLL, pctLL):
    effL = [(100.0 - loss) / 100.0  for loss in lossL]
    
    curve = Curve(plot_type='semilogx', xL=pxdL, yL=effL, marker=MARKERL[i], linestyle='', linewidth=0,
                  label='%g:1'%area_ratio,
                  place_labels_on_line=True, xpos_label=7, dangle_placement=0)
                  
    curveL.append( curve )

    if area_ratio == nasa_epsL[-1]:
        curve.dy_placement=0.005
        msg = 'Markers are digitized NASA data points\nCurves are fitted equations\nArea Ratio from 3:1 to 80:1'
        curve.add_extra_text(label=msg, xpos_label=20, show_label_frame=True,
                             dx_placement=220, dy_placement=-0.01, dangle_placement=0, abs_angle=0,
                             alpha=1, alpha_label=1, label_color='k', label_font_size=12)

    
    i += 1

# plot curve fits

i = 0
for area_ratio, pxdL in zip(nasa_epsL, pxdLL):
    lossL = [eff_bl_NASA( Dt=1.0, Pc=pxd, eps=area_ratio) for pxd in pxdL ]
    
    curve = Curve(plot_type='semilogx', xL=pxdL, yL=lossL, marker='',
                  label='', linecolor=CWheel(i))
                  
    curveL.append( curve )

    i += 1


chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Pc(psia) * Dt(inch)', 
                     ylabel='Boundary Layer Efficiency',
                     show_legend=True, legend_loc='lower right',
                     xmin=5, ymin=.92, xmax=3000)
              


F.make( do_show=True )
