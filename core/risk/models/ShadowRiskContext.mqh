//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowRiskContext.mqh                                  |
//| Layer   : Core / Risk / Models                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Paper-account constraints presented to Risk            |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_MODELS_SHADOWRISKCONTEXT_MQH
#define CORE_RISK_MODELS_SHADOWRISKCONTEXT_MQH

class CShadowRiskContext
  {
public:
   bool   PaperPositionActive;
   double DailyProfitPoints;
   double DrawdownPoints;
   bool   MarketStale;

   CShadowRiskContext()
     {
      Reset();
     }

   void Reset()
     {
      PaperPositionActive=false;
      DailyProfitPoints=0.0;
      DrawdownPoints=0.0;
      MarketStale=false;
     }
  };

#endif
