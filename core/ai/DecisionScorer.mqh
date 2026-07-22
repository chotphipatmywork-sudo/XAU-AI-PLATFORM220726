//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionScorer.mqh                                     |
//| Layer   : Core / AI                                              |
//| Version : 1.0.0                                                  |
//| Purpose : AI Decision Scorer                                     |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DECISIONSCORER_MQH
#define CORE_AI_DECISIONSCORER_MQH

//--------------------------------------------------

class CDecisionScorer
{
public:

   //--------------------------------------------------

   double Score(
      const double signalScore,
      const double confidence)
   {
      double score =
         (signalScore * 0.60) +
         (confidence * 0.40);

      return MathMax(
         0.0,
         MathMin(
            100.0,
            score));
   }

   //--------------------------------------------------

   bool IsStrongBuy(
      const double score)
   {
      return (score >= 85.0);
   }

   //--------------------------------------------------

   bool IsBuy(
      const double score)
   {
      return (score >= 70.0);
   }

   //--------------------------------------------------

   bool IsHold(
      const double score)
   {
      return (score >= 40.0 && score < 70.0);
   }

   //--------------------------------------------------

   bool IsSell(
      const double score)
   {
      return (score < 40.0);
   }

};

#endif