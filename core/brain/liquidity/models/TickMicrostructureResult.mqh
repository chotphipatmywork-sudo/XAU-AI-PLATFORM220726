//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TickMicrostructureResult.mqh                           |
//| Layer   : Brain / Liquidity / Models / Research                 |
//| Version : 1.0.0                                                  |
//| Purpose : Completed-bar tick microstructure research result      |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_MODELS_TICKMICROSTRUCTURERESULT_MQH
#define CORE_BRAIN_LIQUIDITY_MODELS_TICKMICROSTRUCTURERESULT_MQH

class CTickMicrostructureResult
  {
public:
   double TickDirectionImbalance;
   double TickBurstConcentration;
   double MeanSpreadAtr;
   double MaximumSpreadAtr;
   double RealizedTickVolatilityAtr;
   double TickPathEfficiency;
   int    TickCount;
   bool   Valid;

   CTickMicrostructureResult()
     {
      Reset();
     }

   void Reset()
     {
      TickDirectionImbalance=50.0;
      TickBurstConcentration=50.0;
      MeanSpreadAtr=50.0;
      MaximumSpreadAtr=50.0;
      RealizedTickVolatilityAtr=50.0;
      TickPathEfficiency=50.0;
      TickCount=0;
      Valid=false;
     }
  };

#endif

