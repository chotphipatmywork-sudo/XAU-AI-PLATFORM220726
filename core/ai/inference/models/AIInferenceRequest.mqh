//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIInferenceRequest.mqh                                 |
//| Layer   : Core / AI / Inference / Models                        |
//| Version : 1.0.0                                                  |
//| Purpose : Canonical feature request with legacy compatibility    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_INFERENCE_MODELS_AIINFERENCEREQUEST_MQH
#define CORE_AI_INFERENCE_MODELS_AIINFERENCEREQUEST_MQH

#include "../../features/FeatureExtractor.mqh"

class CAIInferenceRequest
  {
public:
   CAIFeatureVector Features;
   double           LegacyTrendScore;
   double           LegacyVolatilityScore;
   double           LegacyLiquidityScore;
   double           LegacySessionScore;

   CAIInferenceRequest()
     {
      LegacyTrendScore=0.0;
      LegacyVolatilityScore=0.0;
      LegacyLiquidityScore=0.0;
      LegacySessionScore=0.0;
     }

   bool FeatureSchemaValid() const
     {
      return(InRange(Features.TrendRegime) &&
             InRange(Features.TrendMomentum) &&
             InRange(Features.TrendSlope) &&
             InRange(Features.VolatilityRegime) &&
             InRange(Features.VolatilityChange) &&
             InRange(Features.LiquidityActivity) &&
             InRange(Features.LiquidityRangePosition) &&
             InRange(Features.LiquiditySweepDirection) &&
             InRange(Features.SessionAsia) &&
             InRange(Features.SessionLondon) &&
             InRange(Features.SessionNewYork) &&
             InRange(Features.SessionProgress));
     }

private:
   bool InRange(const double value) const
     {
      return(MathIsValidNumber(value) && value>=0.0 && value<=100.0);
     }
  };

#endif

