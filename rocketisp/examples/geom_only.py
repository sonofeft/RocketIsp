from rocketisp.geometry import Geometry

# SSME Geometry
G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5,  LnozInp=121,
             RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
             LchmOvrDt=2.4842/2)

G.plot_geometry( title='SSME Profile', png_name='ssme_geom.png', show_grid=True)
G.summ_print()
