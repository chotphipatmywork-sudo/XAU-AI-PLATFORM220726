//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainFeatureAdapter.mqh                                |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Encode Brain output into the canonical AI feature set  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_BRAINFEATUREADAPTER_MQH
#define CORE_AI_BRAINFEATUREADAPTER_MQH

#include "../brain/models/BrainAnalysisResult.mqh"
#include "features/FeatureExtractor.mqh"

class CBrainFeatureAdapter
  {
public:
   bool Extract(const CBrainAnalysisResult &analysis,CAIFeatureVector &features) const
     {
      if(!analysis.Valid)
         return(false);
      features.TrendRegime=MathMax(0.0,MathMin(100.0,analysis.Trend.AITrendRegime));
      features.TrendMomentum=MathMax(0.0,MathMin(100.0,analysis.Trend.AITrendMomentum));
      features.TrendSlope=MathMax(0.0,MathMin(100.0,analysis.Trend.AITrendSlope));
      features.VolatilityRegime=MathMax(0.0,MathMin(100.0,analysis.Volatility.AIVolatilityRegime));
      features.VolatilityChange=MathMax(0.0,MathMin(100.0,analysis.Volatility.AIVolatilityChange));
      features.LiquidityActivity=MathMax(0.0,MathMin(100.0,analysis.Liquidity.Score));
      features.LiquidityRangePosition=MathMax(0.0,MathMin(100.0,analysis.Liquidity.RangePosition));
      features.LiquiditySweepDirection=MathMax(0.0,MathMin(100.0,analysis.Liquidity.SweepDirection));
      features.SessionAsia=(analysis.Session.State==SESSION_ASIA ? 100.0 : 0.0);
      features.SessionLondon=(analysis.Session.State==SESSION_LONDON ? 100.0 : 0.0);
      features.SessionNewYork=(analysis.Session.State==SESSION_NEWYORK ? 100.0 : 0.0);
      features.SessionProgress=MathMax(0.0,MathMin(100.0,analysis.Session.Progress));
      return(true);
     }
  };

#endif
