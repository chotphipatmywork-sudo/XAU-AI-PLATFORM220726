//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ConfirmedSwingStructureResult.mqh                      |
//| Layer   : Brain / Trend / Models / Research                      |
//| Version : 1.0.0                                                  |
//| Purpose : Research-only confirmed swing structure result         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_CONFIRMEDSWINGSTRUCTURERESULT_MQH
#define CORE_BRAIN_TREND_MODELS_CONFIRMEDSWINGSTRUCTURERESULT_MQH

class CConfirmedSwingStructureResult
  {
public:
   bool   Valid;
   double StructureDirection;
   double BreakDirection;
   double ChochDirection;
   double RangePosition;
   double LatestSwingHigh;
   double LatestSwingLow;

   CConfirmedSwingStructureResult(void)
     {
      Reset();
     }

   void Reset(void)
     {
      Valid=false;
      StructureDirection=50.0;
      BreakDirection=50.0;
      ChochDirection=50.0;
      RangePosition=50.0;
      LatestSwingHigh=0.0;
      LatestSwingLow=0.0;
     }
  };

#endif
