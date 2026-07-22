//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LabelCalibrationReport.mqh                             |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Summarize one triple-barrier label calibration trial   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_LABELCALIBRATIONREPORT_MQH
#define CORE_AI_MODELS_LABELCALIBRATIONREPORT_MQH

class CLabelCalibrationReport
  {
public:
   int    HorizonBars;
   int    AtrPeriod;
   double BarrierAtrMultiplier;
   int    SampleCount;
   int    BuyCount;
   int    HoldCount;
   int    SellCount;
   int    ExcludedCount;

   CLabelCalibrationReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      HorizonBars=0;
      AtrPeriod=0;
      BarrierAtrMultiplier=0.0;
      SampleCount=0;
      BuyCount=0;
      HoldCount=0;
      SellCount=0;
      ExcludedCount=0;
     }

   double HoldRatio(void) const
     {
      if(SampleCount<=0)
         return(0.0);
      return((double)HoldCount/(double)SampleCount);
     }
  };

#endif
