//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestVolatilityFeatureRegime.mq5                        |
//| Layer   : Tests / Brain / Volatility                             |
//| Version : 1.0.0                                                  |
//| Purpose : AI volatility regime and change smoke test             |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/VolatilityAnalyzer.mqh"

int OnInit()
  {
   CVolatilityContext context;
   context.Symbol=_Symbol;
   context.Timeframe=PERIOD_M15;
   context.Bars=Bars(_Symbol,PERIOD_M15);
   context.Shift=0;
   CVolatilityAnalyzer analyzer;
   const CVolatilityResult result=analyzer.Analyze(context);
   const bool valid=(result.ATR>0.0 &&
                     result.AIVolatilityRegime>=0.0 &&
                     result.AIVolatilityRegime<=100.0 &&
                     result.AIVolatilityChange>=0.0 &&
                     result.AIVolatilityChange<=100.0);
   Print("Volatility ATR/regime/change: ",result.ATR,"/",
         result.AIVolatilityRegime,"/",result.AIVolatilityChange);
   Print("AI volatility feature valid: ",valid);
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
