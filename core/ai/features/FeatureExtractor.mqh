//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : FeatureExtractor.mqh                                   |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : AI Feature Extraction                                  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_LEARNING_FEATUREEXTRACTOR_MQH
#define CORE_AI_LEARNING_FEATUREEXTRACTOR_MQH

//--------------------------------------------------
// AI Feature Vector
//--------------------------------------------------

class CAIFeatureVector
{
public:

   double TrendRegime;

   double TrendMomentum;

   double TrendSlope;

   double VolatilityRegime;

   double VolatilityChange;

   double LiquidityActivity;

   double LiquidityRangePosition;

   double LiquiditySweepDirection;

   double SessionAsia;

   double SessionLondon;

   double SessionNewYork;

   double SessionProgress;

public:

   CAIFeatureVector()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      TrendRegime    = 0.0;
      TrendMomentum  = 0.0;
      TrendSlope     = 0.0;
      VolatilityRegime = 0.0;
      VolatilityChange = 0.0;
      LiquidityActivity = 0.0;
      LiquidityRangePosition = 0.0;
      LiquiditySweepDirection = 0.0;
      SessionAsia    = 0.0;
      SessionLondon  = 0.0;
      SessionNewYork = 0.0;
      SessionProgress = 0.0;
   }

};


//--------------------------------------------------
// Feature Extractor
//--------------------------------------------------

class CFeatureExtractor
{

public:

   //--------------------------------------------------

   CAIFeatureVector Extract(
      const double trend_regime,
      const double trend_momentum,
      const double trend_slope,
      const double volatility_regime,
      const double volatility_change,
      const double liquidity_activity,
      const double liquidity_range_position,
      const double liquidity_sweep_direction,
      const double session_asia,
      const double session_london,
      const double session_new_york,
      const double session_progress)
   {

      CAIFeatureVector feature;

      feature.TrendRegime = trend_regime;

      feature.TrendMomentum = trend_momentum;

      feature.TrendSlope = trend_slope;

      feature.VolatilityRegime = volatility_regime;

      feature.VolatilityChange = volatility_change;

      feature.LiquidityActivity = liquidity_activity;

      feature.LiquidityRangePosition = liquidity_range_position;

      feature.LiquiditySweepDirection = liquidity_sweep_direction;

      feature.SessionAsia = session_asia;

      feature.SessionLondon = session_london;

      feature.SessionNewYork = session_new_york;

      feature.SessionProgress = session_progress;

      return feature;

   }

};

#endif

//+------------------------------------------------------------------+
