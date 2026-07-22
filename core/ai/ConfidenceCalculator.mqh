//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ConfidenceCalculator.mqh                               |
//| Layer   : Core / AI                                              |
//| Version : 2.0.0                                                  |
//| Purpose : AI Confidence Calculator                               |
//+------------------------------------------------------------------+

#ifndef CORE_AI_CONFIDENCECALCULATOR_MQH
#define CORE_AI_CONFIDENCECALCULATOR_MQH

//--------------------------------------------------

class CConfidenceCalculator
{
public:

   //--------------------------------------------------

   double Calculate(
      const double trendScore,
      const double volatilityScore,
      const double liquidityScore,
      const double sessionScore)
   {
      double confidence =
         (trendScore +
          volatilityScore +
          liquidityScore +
          sessionScore) / 4.0;

      confidence =
         MathMax(
            0.0,
            MathMin(
               100.0,
               confidence));

      return confidence;
   }

   //--------------------------------------------------

   bool IsHighConfidence(
      const double confidence)
   {
      return (confidence >= 80.0);
   }

   //--------------------------------------------------

   bool IsMediumConfidence(
      const double confidence)
   {
      return (confidence >= 60.0);
   }

   //--------------------------------------------------

   bool IsLowConfidence(
      const double confidence)
   {
      return (confidence < 60.0);
   }

};

#endif