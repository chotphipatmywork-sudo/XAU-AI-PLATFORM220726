//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveHybridSetupConfig.mqh                         |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.1.0                                                  |
//| Purpose : Frozen CR-013 objective setup and reclaim thresholds    |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_SETUP_CONFIG_MQH
#define XAU_OBJECTIVE_SETUP_CONFIG_MQH

class CObjectiveHybridSetupConfig
  {
public:
   double BullishMinimum;
   double BearishMaximum;
   double PoiTolerancePoints;
   double PoiToleranceAtrFraction;
   double SweepPenetrationPoints;
   double SweepPenetrationAtrFraction;
   double MinimumReclaimAtr;
   double StopBufferAtrFraction;

   CObjectiveHybridSetupConfig()
     {
      Reset();
     }

   void Reset()
     {
      BullishMinimum=55.0;
      BearishMaximum=45.0;
      PoiTolerancePoints=10.0;
      PoiToleranceAtrFraction=0.10;
      SweepPenetrationPoints=1.0;
      SweepPenetrationAtrFraction=0.02;
      MinimumReclaimAtr=0.10;
      StopBufferAtrFraction=0.10;
     }

   bool Valid() const
     {
      return(MathIsValidNumber(BullishMinimum) &&
             MathIsValidNumber(BearishMaximum) &&
             MathIsValidNumber(PoiTolerancePoints) &&
             MathIsValidNumber(PoiToleranceAtrFraction) &&
             MathIsValidNumber(SweepPenetrationPoints) &&
             MathIsValidNumber(SweepPenetrationAtrFraction) &&
             MathIsValidNumber(MinimumReclaimAtr) &&
             MathIsValidNumber(StopBufferAtrFraction) &&
             BullishMinimum>50.0 && BullishMinimum<=100.0 &&
             BearishMaximum>=0.0 && BearishMaximum<50.0 &&
             BearishMaximum<BullishMinimum &&
             PoiTolerancePoints>0.0 &&
             PoiToleranceAtrFraction>0.0 &&
             SweepPenetrationPoints>0.0 &&
             SweepPenetrationAtrFraction>0.0 &&
             MinimumReclaimAtr>0.0 &&
             StopBufferAtrFraction>0.0);
     }
  };

#endif
