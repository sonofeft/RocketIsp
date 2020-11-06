
"""
Thrust Chamber Efficiencies
"""

from rocketisp.efficiency.eff_pulsing import eff_pulse
from rocketisp.efficiency.eff_divergence import eff_div
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA
from rocketisp.efficiency.calc_All_fracKin import calc_fracKin

class ThrustChamberEfficiency:
    
    def __init__(self, ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
                 effML=None, effVap=None, effHL=None, Em=0.8,
                 effDiv=None, effTP=None, effKin=None, effBL=None,
                 effPulse=1.0, pulse_quality=0.8, pulse_sec=0.5, # assume chamber is not pulsing 
                 effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
                 isRegenCham=0, isRegenNoz=0, # regen cooling decreases boundary layer loss.
                 effML_method    ='Mixing Angle',
                 effEm_method    ='Rule Of Thumb',
                 effVap_method   ='ELES',
                 effHL_method    ='ELES',
                 effDiv_method   ='TDK Correlation',
                 effTP_method    ='Unity',
                 effKin_method   ='TDK Correlation',
                 effBL_method    ='NASA SP8120',
                 effFFC_method   ='Stream Tube',
                 effPulse_method ='Historical'):
        """If input efficiency is None, use designated method to calculate it."""
        
        # save the input values
        self.effML_inp     = effML        # inter-element mixing
        self.Em_inp        = min(1.0, Em) # intra-element mixing parameter for injector
        self.effVap_inp    = effVap
        self.effHL_inp     = effHL
        self.effDiv_inp    = effDiv
        self.effTP_inp     = effTP
        self.effKin_inp    = effKin
        self.effBL_inp     = effBL
        self.effPulse_inp  = effPulse
        self.pulse_quality = max(0.0, min(1.0,pulse_quality)) # 0=worst, 1.0=best
        self.pulse_sec     = pulse_sec   # duration of average pulse (sec)
        
        self.effML_method  = effML_method
        self.effEm_method  = effEm_method
        self.effVap_method = effVap_method
        self.effHL_method  = effHL_method
        self.effDiv_method = effDiv_method
        self.effTP_method  = effTP_method
        self.effKin_method = effKin_method
        self.effBL_method  = effBL_method
        
    def calc(self):
        # use input value (if present) or calc with desired method
        
        # ============== Pulsing Efficiency ==============
        if self.effPulse_inp is None:
            if self.effPulse_method == "Historical":
                self.effPulse = eff_pulse( pulse_sec=self.pulse_sec, pulse_quality=self.pulse_quality)
            else:
                raise('effPulse_method "%s" is not recognized'%self.effPulse_method )
        else:
            self.effPulse = self.effPulse_inp
        
        # ============== inter-element Mixing Efficiency ================
        # inter-element mixing
        if self.effML_inp is None:
            if self.effML_method == "Mixing Angle":
                self.effML = 1.0
            else:
                raise('effML_method "%s" is not recognized'%self.effML_method )
        else:
            self.effML = self.effML_inp
        
        # intra-element mixing requires knowledge of Em parameter for injector type.
        if self.Em_inp >= 1.0:
            # assume perfect mixing if Em == 1.0
            self.effEm = 1.0
        else:
            # given an Em, calculate etaEm
            if self.effEm_method == "Rule Of Thumb":
                self.effEm = 1.0
            else:
                raise('effEm_method "%s" is not recognized'%self.effEm_method )
        
            
        # ============== Vaporization Efficiency ================
        if self.effVap_inp is None:
            if self.effVap_method == "ELES":
                self.effVap = 1.0
            else:
                raise('effVap_method "%s" is not recognized'%self.effVap_method )
        else:
            self.effVap = self.effVap_inp
            
        # ============== Heat Loss Efficiency ================
        if self.effHL_inp is None:
            if self.effHL_method == "ELES":
                self.effHL = 1.0
            else:
                raise('effHL_method "%s" is not recognized'%self.effHL_method )
        else:
            self.effHL = self.effHL_inp
            
        # ============== Divergence Efficiency ================
        if self.effDiv_inp is None:
            if self.effDiv_method == "TDK Correlation":
                self.effDiv = 1.0
            else:
                raise('effDiv_method "%s" is not recognized'%self.effDiv_method )
        else:
            self.effDiv = self.effDiv_inp
            
        # ============== Two Phase Efficiency ================
        if self.effTP_inp is None:
            if self.effTP_method == "Unity":
                self.effTP = 1.0
            else:
                raise('effTP_method "%s" is not recognized'%self.effTP_method )
        else:
            self.effTP = self.effTP_inp
            
        # ============== Kinetic Efficiency ================
        if self.effKin_inp is None:
            if self.effKin_method == "TDK Correlation":
                self.effKin = 1.0
            else:
                raise('effKin_method "%s" is not recognized'%self.effKin_method )
        else:
            self.effKin = self.effKin_inp
            
        # ============== Boundary Layer Efficiency ================
        if self.effBL_inp is None:
            if self.effBL_method == "NASA SP8120":
                self.effBL = 1.0
            else:
                raise('effBL_method "%s" is not recognized'%self.effBL_method )
        else:
            self.effBL = self.effBL_inp

    
if __name__ == "__main__":
    
    from rocketcea.cea_obj import CEA_Obj
    
    ceaObj = CEA_Obj(oxName='N2O4', fuelName='MMH', useFastLookup=0)

    tceff = ThrustChamberEfficiency( ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
        effML=None, effVap=None, effHL=None, Em=0.8,
        effDiv=None, effTP=None, effKin=None, effBL=None,
        effPulse=1.0, pulse_quality=0.8, pulse_sec=0.5, # assume chamber is not pulsing 
        effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
        isRegenCham=0, isRegenNoz=0, # regen cooling decreases boundary layer loss.
        effML_method    ='Mixing Angle',
        effEm_method    ='Rule Of Thumb',
        effVap_method   ='ELES',
        effHL_method    ='ELES',
        effDiv_method   ='TDK Correlation',
        effTP_method    ='Unity',
        effKin_method   ='TDK Correlation',
        effBL_method    ='NASA SP8120',
        effFFC_method   ='Stream Tube',
        effPulse_method ='Historical')
        
        