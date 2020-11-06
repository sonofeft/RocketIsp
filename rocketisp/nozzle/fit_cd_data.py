from xymath.dataset import DataSet
from xymath.linfit import LinCurveFit
from xymath.xy_job import XY_Job

"""
# Rup=0.5,  std=5.48718e-06
cd_050 =  1/(1.0410141095741985 - 0.018737945262767248*gamma)
# Rup=0.75,  std=1.28366e-05
cd_075 =  1/(1.0211820293860214 - 0.006064881097850447*gamma)
# Rup=1,  std=1.01453e-05
cd_100 =  1/(1.0125848593169495 - 0.002058029259787154*gamma)
# Rup=1.5,  std=4.85485e-06
cd_150 =  1/(1.0059285328940355 - 0.00011367842090816805/gamma)
# Rup=2,  std=1.52664e-07
cd_200 =  0.9957021782441166 + 0.0006720167698767546/gamma

"""

gammaL = [1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4]

cdD = {} # index=RWTU, value=CD
cdD[0.5] = [0.9800142, 0.9809054, 0.981803, 0.9827062, 0.9836141, 0.9845261, 0.9854414]
cdD[0.75] = [0.9857159, 0.9859911, 0.9862749, 0.9865668, 0.9868662, 0.9871727, 0.9874859]
cdD[1] = [0.9897993, 0.989885, 0.989977, 0.9900752, 0.9901793, 0.990289, 0.990404]
cdD[1.5] = [0.9942151, 0.9942037, 0.9941956, 0.9941907, 0.9941889, 0.99419, 0.9941941]
cdD[2] = [0.9963129, 0.9962867, 0.9962624, 0.9962398, 0.996219, 0.9961998, 0.9961823]

RupL = sorted( list( cdD.keys() ) )

for Rup in RupL:
    job = XY_Job()
    yL = cdD[Rup]
    job.define_dataset( gammaL, yL, xName='gamma', yName='Cd')
    ordered_resultL = job.fit_dataset_to_common_eqns( run_both=1, sort_by_pcent=1, max_terms=2)
    print('# Rup=%g,  std=%g'%(Rup, job.linfit.std))
    print( 'cd_%s = '%(str(int(100*Rup)).zfill(3),), job.linfit.get_eqn_str_w_numbs() )
