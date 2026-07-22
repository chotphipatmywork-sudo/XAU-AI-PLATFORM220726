//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : FeatureNormalizer.mqh                                  |
//| Layer   : Core / AI / Features                                   |
//| Version : 4.0.0                                                  |
//| Purpose : AI Feature Normalizer                                  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_FEATURES_FEATURENORMALIZER_MQH
#define CORE_AI_FEATURES_FEATURENORMALIZER_MQH

#include "FeatureExtractor.mqh"

//--------------------------------------------------
// Feature Normalizer
//--------------------------------------------------

class CFeatureNormalizer
{

private:

   bool m_initialized;

public:

   //--------------------------------------------------

   CFeatureNormalizer()
   {
      m_initialized = false;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      m_initialized = true;

      return true;
   }

   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }

   //--------------------------------------------------
   // Normalize Single Value
   //--------------------------------------------------

   double Normalize(
      const double value) const
   {

      return MathMax(
         0.0,
         MathMin(
            100.0,
            value));

   }

   //--------------------------------------------------
   // Normalize Feature Vector
   //--------------------------------------------------

   bool NormalizeVector(
      CAIFeatureVector &features)
   {

      if(!m_initialized)
         return false;

      features.TrendRegime = Normalize(features.TrendRegime);

      features.TrendMomentum = Normalize(features.TrendMomentum);

      features.TrendSlope = Normalize(features.TrendSlope);

      features.VolatilityRegime = Normalize(features.VolatilityRegime);

      features.VolatilityChange = Normalize(features.VolatilityChange);

      features.LiquidityActivity = Normalize(features.LiquidityActivity);

      features.LiquidityRangePosition = Normalize(features.LiquidityRangePosition);

      features.LiquiditySweepDirection = Normalize(features.LiquiditySweepDirection);

      features.SessionAsia = Normalize(features.SessionAsia);

      features.SessionLondon = Normalize(features.SessionLondon);

      features.SessionNewYork = Normalize(features.SessionNewYork);

      features.SessionProgress = Normalize(features.SessionProgress);

      return true;

   }

   //--------------------------------------------------
   // Process Feature
   //--------------------------------------------------

   CAIFeatureVector Process(
      const CAIFeatureVector &source)
   {

      CAIFeatureVector result;

      result.TrendRegime = source.TrendRegime;

      result.TrendMomentum = source.TrendMomentum;

      result.TrendSlope = source.TrendSlope;

      result.VolatilityRegime = source.VolatilityRegime;

      result.VolatilityChange = source.VolatilityChange;

      result.LiquidityActivity = source.LiquidityActivity;

      result.LiquidityRangePosition = source.LiquidityRangePosition;

      result.LiquiditySweepDirection = source.LiquiditySweepDirection;

      result.SessionAsia = source.SessionAsia;

      result.SessionLondon = source.SessionLondon;

      result.SessionNewYork = source.SessionNewYork;

      result.SessionProgress = source.SessionProgress;

      NormalizeVector(result);

      return result;

   }

};

#endif
