//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SignalFusion.mqh                                       |
//| Layer   : Core / AI                                              |
//| Version : 2.0.0                                                  |
//| Purpose : Signal Fusion Engine                                   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_SIGNALFUSION_MQH
#define CORE_AI_SIGNALFUSION_MQH

//--------------------------------------------------

class CSignalFusion
{
public:

   //--------------------------------------------------

   double CalculateScore(
      const double trendScore,
      const double volatilityScore,
      const double liquidityScore,
      const double sessionScore)
   {
      // Equal weighting (ADR-005)
      double score =
         (trendScore +
          volatilityScore +
          liquidityScore +
          sessionScore) / 4.0;

      return MathMax(
         0.0,
         MathMin(
            100.0,
            score));
   }

   //--------------------------------------------------

   bool IsBullish(
      const double score)
   {
      return (score >= 70.0);
   }

   //--------------------------------------------------

   bool IsBearish(
      const double score)
   {
      return (score <= 30.0);
   }

   //--------------------------------------------------

   bool IsNeutral(
      const double score)
   {
      return (score > 30.0 && score < 70.0);
   }

};

#endif