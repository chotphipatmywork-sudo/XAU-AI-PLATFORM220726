//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestBrainFeatureAdapter.mq5                            |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 4.0.0                                                  |
//| Purpose : Feature Contract 4.0 Brain projection smoke test       |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/BrainFeatureAdapter.mqh"

int OnInit()
  {
   CBrainAnalysisResult analysis;
   analysis.Valid=true;
   analysis.Trend.AITrendRegime=90.0;
   analysis.Trend.AITrendMomentum=70.0;
   analysis.Trend.AITrendSlope=40.0;
   analysis.Volatility.AIVolatilityRegime=55.0;
   analysis.Volatility.AIVolatilityChange=60.0;
   analysis.Liquidity.Score=35.0;
   analysis.Liquidity.RangePosition=80.0;
   analysis.Liquidity.SweepDirection=100.0;
   analysis.Session.State=SESSION_LONDON;
   analysis.Session.Progress=25.0;
   CAIFeatureVector features;
   CBrainFeatureAdapter adapter;
   if(!adapter.Extract(analysis,features))
     {
      Print("Brain feature adapter extraction failed");
      return(INIT_FAILED);
     }
   const bool valid=(MathAbs(features.TrendRegime-90.0)<0.000001 &&
                     MathAbs(features.TrendMomentum-70.0)<0.000001 &&
                     MathAbs(features.TrendSlope-40.0)<0.000001 &&
                     MathAbs(features.VolatilityRegime-55.0)<0.000001 &&
                     MathAbs(features.VolatilityChange-60.0)<0.000001 &&
                     MathAbs(features.LiquidityActivity-35.0)<0.000001 &&
                     MathAbs(features.LiquidityRangePosition-80.0)<0.000001 &&
                     MathAbs(features.LiquiditySweepDirection-100.0)<0.000001 &&
                     MathAbs(features.SessionAsia-0.0)<0.000001 &&
                     MathAbs(features.SessionLondon-100.0)<0.000001 &&
                     MathAbs(features.SessionNewYork-0.0)<0.000001 &&
                     MathAbs(features.SessionProgress-25.0)<0.000001);
   Print("Brain feature projection TREND3/VOLATILITY2/LIQUIDITY3/SESSION4: ",
         features.TrendRegime,"/",features.TrendMomentum,"/",features.TrendSlope,"/",
         features.VolatilityRegime,"/",features.VolatilityChange,"/",
         features.LiquidityActivity,"/",features.LiquidityRangePosition,"/",
         features.LiquiditySweepDirection,"/",features.SessionAsia,"/",
         features.SessionLondon,"/",features.SessionNewYork,"/",features.SessionProgress);
   Print("Brain feature projection valid: ",valid);
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
