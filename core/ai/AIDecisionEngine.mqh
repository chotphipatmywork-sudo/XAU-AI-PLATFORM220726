//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIDecisionEngine.mqh                                   |
//| Layer   : Core / AI                                              |
//| Version : 2.0.0                                                  |
//| Purpose : AI Decision Engine                                     |
//+------------------------------------------------------------------+

#ifndef CORE_AI_AIDECISIONENGINE_MQH
#define CORE_AI_AIDECISIONENGINE_MQH

#include "SignalFusion.mqh"
#include "ConfidenceCalculator.mqh"
#include "DecisionScorer.mqh"

#include "models/AIDecision.mqh"
#include "validation/AIDecisionValidator.mqh"

//--------------------------------------------------

class CAIDecisionEngine
{
private:

   CSignalFusion          m_fusion;
   CConfidenceCalculator  m_confidence;
   CDecisionScorer        m_scorer;
   CAIDecisionValidator   m_validator;

public:

   //--------------------------------------------------

   CAIDecisionEngine()
   {
   }

   //--------------------------------------------------

   CAIDecision Evaluate(
      const double trendScore,
      const double volatilityScore,
      const double liquidityScore,
      const double sessionScore)
   {
      CAIDecision decision;

      double signalScore =
         m_fusion.CalculateScore(
            trendScore,
            volatilityScore,
            liquidityScore,
            sessionScore);

      double confidence =
         m_confidence.Calculate(
            trendScore,
            volatilityScore,
            liquidityScore,
            sessionScore);

      double score =
         m_scorer.Score(
            signalScore,
            confidence);

      decision.Score      = score;
      decision.Confidence = confidence;
      decision.Timestamp  = TimeCurrent();
      decision.Symbol     = _Symbol;
      decision.Timeframe  = PERIOD_CURRENT;

      //--------------------------------------------------
      // Decision Mapping
      //--------------------------------------------------

      if(m_scorer.IsStrongBuy(score))
      {
         decision.Type   = AI_DECISION_BUY;
         decision.Action = AI_ACTION_BUY;
      }
      else if(m_scorer.IsBuy(score))
      {
         decision.Type   = AI_DECISION_BUY;
         decision.Action = AI_ACTION_BUY;
      }
      else if(m_scorer.IsHold(score))
      {
         decision.Type   = AI_DECISION_HOLD;
         decision.Action = AI_ACTION_HOLD;
      }
      else
      {
         decision.Type   = AI_DECISION_SELL;
         decision.Action = AI_ACTION_SELL;
      }

      //--------------------------------------------------
      // Validation
      //--------------------------------------------------

      if(!m_validator.Validate(decision))
      {
         decision.Reset();
         return decision;
      }

      decision.Valid = true;

      return decision;
   }
};

#endif