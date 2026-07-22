//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendResult.mqh                                        |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 2.3.0                                                  |
//| Purpose : Final Trend Analysis Result                            |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_TRENDRESULT_MQH
#define CORE_BRAIN_TREND_MODELS_TRENDRESULT_MQH

//--------------------------------------------------
// Trend Direction
//--------------------------------------------------

enum ENUM_TREND_DIRECTION
{
   TREND_UNKNOWN = 0,
   TREND_BULLISH,
   TREND_BEARISH,
   TREND_SIDEWAYS
};

//--------------------------------------------------
// Trend Result
//--------------------------------------------------

class CTrendResult
{
public:

   ENUM_TREND_DIRECTION Direction;

   double Strength;

   double AITrendScore;

   double AITrendRegime;

   double AITrendMomentum;

   double AITrendSlope;

   double Confidence;

   bool Valid;

   CTrendResult()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Direction  = TREND_UNKNOWN;
      Strength   = 0.0;
      AITrendScore    = 50.0;
      AITrendRegime   = 50.0;
      AITrendMomentum = 50.0;
      AITrendSlope    = 50.0;
      Confidence = 0.0;
      Valid      = false;
   }
};

#endif
