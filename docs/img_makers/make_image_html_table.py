'''
print( template.format( width='100%', image1_width='50%', image2_width_stmt='',  #'; width="80%"',
                        image1_label='xxx', image1_name='xxx',
                        image2_label='xxx', image2_name='xxx' ) )
'''


template = """
.. raw:: html

    <table width="{width}">
    <tr>
    <th style="text-align:center;"> {image1_label} </th>
    <th style="text-align:center;"> {image2_label} </th>
    </tr>
    <tr>
    <td width="{image1_width}">
    <a class="reference internal image-reference" href="./_static/{image1_name}">
    <img src="./_static/{image1_name}">
    </a>
    </td>
    <td>
    <a class="reference internal image-reference" href="./_static/{image2_name}">
    <img src="./_static/{image2_name}" {image2_width_stmt}>
    </a>
    </td>
    </tr>
    <tr>
    <td colspan="2" style="text-align:center;">
    <p><cite>Click image to see full size</cite></p>
    </td>
    </tr>
    </table>
"""


print( template.format( width='100%', image1_width='50%', image2_width_stmt='',
                        image1_label='RdwnThroat Sensitivity', image1_name='effdiv_monte_Rd.png',
                        image2_label='Rthrt Sensitivity', image2_name='effdiv_monte_Rthrt.png' ) )



print( template.format( width='100%', image1_width='50%', image2_width_stmt='',
                        image1_label='Throat Radius=1 inch', image1_name='cmp_cd_calcs_pc.png',
                        image2_label='Chamber Pressure=200 psia', image2_name='cmp_cd_calcs_rthrt.png' ) )

print( template.format( width='100%', image1_width='50%', image2_width_stmt='',
                        image1_label='High Pc, Large Throat', image1_name='cmp_cd_calcs_best.png',
                        image2_label='Low Pc, Small Throat', image2_name='cmp_cd_calcs_worst.png' ) )



print( template.format( width='100%', image1_width='40%', image2_width_stmt='; width="60%"',
                        image1_label='NASA SP 8120', image1_name='At_flow_vs_geom_v2.jpg',
                        image2_label='NASA 33-548', image2_name='Cd_NASA_1973.jpg' ) )


print( template.format( width='100%', image1_width='50%', image2_width_stmt='',
                        image1_label='NASA SP 8120 Loss', image1_name='viscous_drag_loss.jpg',
                        image2_label='Curve Fit SP 8120', image2_name='nasa_sp8120_bl_eff.png' ) )


print( template.format( width='100%', image1_width='50%', image2_width_stmt='',
                        image1_label='Pc=100 psia', image1_name='effbl_parametrics_Pc100.png',
                        image2_label='Pc=1000 psia', image2_name='effbl_parametrics_Pc1000.png' ) )

print( template.format( width='100%', image1_width='50%',  image2_width_stmt='',
                        image1_label='xxx', image1_name='xxx',
                        image2_label='xxx', image2_name='xxx' ) )



print( template.format( width='100%', image1_width='60%', image2_width_stmt='',
                        image1_label='TDK Runs', image1_name='effdiv_simple.png',
                        image2_label='CPIA 246', image2_name='etadiv_cpia_246_pg3_2_4b.jpg' ) )

