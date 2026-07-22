//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PricePathStateResult.mqh                               |
//| Layer   : Brain / Trend / Models / Research                      |
//| Version : 1.0.0                                                  |
//| Purpose : Hold bounded completed price-path research values      |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_PRICEPATHSTATERESULT_MQH
#define CORE_BRAIN_TREND_MODELS_PRICEPATHSTATERESULT_MQH

class CPricePathStateResult
  {
public:
   bool   Valid;
   double PathDirectionalEfficiency;
   double UpCloseRatio;
   double DirectionalRunBalance;
   double ReturnSignPersistence;
   double PathTravelAtr;
   double RangeEfficiency;
   double RangeExpansion;

   CPricePathStateResult(void)
     {
      Reset();
     }

   void Reset(void)
     {
      Valid=false;
      PathDirectionalEfficiency=50.0;
      UpCloseRatio=50.0;
      DirectionalRunBalance=50.0;
      ReturnSignPersistence=50.0;
      PathTravelAtr=50.0;
      RangeEfficiency=50.0;
      RangeExpansion=50.0;
     }
  };

#endif
