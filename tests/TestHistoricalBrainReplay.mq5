//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalBrainReplay.mq5                          |
//| Purpose : Historical Brain replay smoke test                     |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/HistoricalBrainReplay.mqh"

void OnStart()
  {
   CHistoricalBrainReplay replay;
   const CBrainAnalysisResult result=replay.Analyze(_Symbol,PERIOD_M15,20);
   Print("Historical Brain valid: ",result.Valid,
         " trend: ",result.Trend.Strength,
         " volatility: ",result.Volatility.Confidence,
         " liquidity: ",result.Liquidity.Score,
         " session: ",result.Session.Confidence);
  }
