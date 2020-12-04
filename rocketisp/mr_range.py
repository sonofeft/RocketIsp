
class MRrange:
    
    def __init__(self, ispObj, Pc=500., eps=20., 
                 edge_frac=0.97):
        
        self.Pc = Pc
        self.eps = eps
        self.edge_frac = edge_frac
        self.ispObj = ispObj
        self.MRstoic = self.ispObj.getMRforER( ERr=1.0 )
        self.MRstep = max( self.MRstoic/30.0, 0.01 )
        #print('MRstoic=',self.MRstoic, '      MRstep =',self.MRstep)

        IspVac = self.ispObj.get_Isp( Pc=Pc, MR=self.MRstoic, eps=eps)
        self.dataL = [(self.MRstoic, IspVac)]
        
        self.peakIsp = IspVac
        self.peakMR  = self.MRstoic
        
        self.mr_min = self.MRstoic - self.MRstep
        self.mr_max = self.MRstoic + self.MRstep
        
        self.IspAtMRmin = self.add_mr( self.mr_min )
        self.IspAtMRmax = self.add_mr( self.mr_max )
        
        for _ in range(1000):
            mr = self.mr_min - self.MRstep
            if mr <= 0.0:
                break
            IspVac = self.add_mr( mr )
            if IspVac / self.peakIsp < self.edge_frac:
                break
        #print('Min MR=',self.mr_min,'   IspAtMRmin=', self.IspAtMRmin)

        # find MR max
        for _ in range(1000):
            mr = self.mr_max + self.MRstep
            IspVac = self.add_mr( mr )
            
            if IspVac / self.peakIsp < self.edge_frac:
                break
        #print('Max MR=',self.mr_max,'   IspAtMRmax=', self.IspAtMRmax)
        #print('Peak MR=',self.peakMR,'   peakIsp=', self.peakIsp)
        
        self.dataL.sort() # sort in MR order
        
        # prune list to single overhang values on each end.
        new_dataL = []
        IspCutoff = self.edge_frac * self.peakIsp
        def is_keeper( i ):
            if i==0:
                mrp1, Ispp1 = self.dataL[i+1]
                if Ispp1 >= IspCutoff:
                    return True
                    
            elif i==len( self.dataL ) - 1:
                mrm1, Ispm1 = self.dataL[i-1]
                if Ispm1 >= IspCutoff:
                    return True
            else:
                mr, Isp = self.dataL[i]
                if Isp >= IspCutoff:
                    return True
                mrp1, Ispp1 = self.dataL[i+1]
                if Ispp1 >= IspCutoff:
                    return True
                mrm1, Ispm1 = self.dataL[i-1]
                if Ispm1 >= IspCutoff:
                    return True
            return False
            
        for i,(mr, IspVac) in enumerate(self.dataL):
            if is_keeper( i ):
                new_dataL.append( (mr, IspVac) )
        
        # approximate MR of both ends with linear interpolation
        mr1, Is1 = new_dataL[0]
        mr2, Is2 = new_dataL[1]
        mr = mr1 + (mr2-mr1)*(IspCutoff-Is1)/(Is2-Is1)
        new_dataL[0] = (mr, self.ispObj.get_Isp( Pc=self.Pc, MR=mr, eps=self.eps))
        
        mr1, Is1 = new_dataL[-2]
        mr2, Is2 = new_dataL[-1]
        mr = mr1 + (mr2-mr1)*(IspCutoff-Is1)/(Is2-Is1)
        new_dataL[-1] = (mr, self.ispObj.get_Isp( Pc=self.Pc, MR=mr, eps=self.eps))

        
        # set dataL to just the keepers
        self.dataL = new_dataL
    
    def get_mr_range(self):
        return self.dataL[0][0], self.dataL[-1][0]
    
    def get_mr_list(self):
        return [mr for mr,_ in self.dataL]
        
    def add_mr(self, mr):
        
        IspVac = self.ispObj.get_Isp( Pc=self.Pc, MR=mr, eps=self.eps)
        if mr<self.mr_min:
            self.mr_min = mr
            self.IspAtMRmin = IspVac
        if mr>self.mr_max:
            self.mr_max = mr
            self.IspAtMRmax = IspVac
        
        if IspVac > self.peakIsp:
            self.peakIsp = IspVac
            self.peakMR = mr
            
        self.dataL.append( (mr, IspVac) )
            
        return IspVac

if __name__ == "__main__":    
    from rocketcea.cea_obj import CEA_Obj
    
    #ispObj = ispObj = CEA_Obj( oxName='LOX', fuelName='LH2')
    ispObj = ispObj = CEA_Obj( oxName='N2O4', fuelName='MMH')
    #ispObj = ispObj = CEA_Obj( oxName='N2O4', fuelName='N2H4')

    mrr = MRrange(ispObj, Pc=500., eps=20.)

    for mr,IspVac in mrr.dataL:
        print( 'MR=%6.2f  Isp=%8.3f'%(mr, IspVac), '%9.5f'%(IspVac/mrr.peakIsp,) )


    print('MR List:', mrr.get_mr_list())