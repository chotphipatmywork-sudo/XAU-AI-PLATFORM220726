//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveSetupResearchProvider.mqh                    |
//| Layer   : Core / AI / Strategy                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Tester-only Objective Setup decision and plan provider |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_SETUP_PROVIDER_MQH
#define XAU_OBJECTIVE_SETUP_PROVIDER_MQH

#include "ObjectiveMultiTimeframeSetupAdapter.mqh"
#include "HybridRuleSetupEngine.mqh"
#include "StructureAwareTradePlanner.mqh"
#include "../models/AIDecision.mqh"

class CObjectiveSetupResearchProvider
  {
private:
   CObjectiveMultiTimeframeSetupAdapter m_adapter;
   CHybridRuleSetupEngine                m_setupEngine;
   CStructureAwareTradePlanner          m_planner;
   bool                                 m_initialized;

   double Bounded(const double value) const
     {
      return(MathMax(0.0,MathMin(100.0,value)));
     }

public:
   CObjectiveSetupResearchProvider()
     {
      m_initialized=false;
     }

   bool Initialize()
     {
      m_initialized=true;
      return(true);
     }

   bool Evaluate(const CObjectiveMultiTimeframeSetupInput &source,
                 CAIDecision &decision,
                 CStructureAwareTradePlan &plan,
                 CObjectiveMultiTimeframeSetupEvidence &evidence,
                 bool &planAvailable,
                 string &reason)
     {
      decision.Reset();
      plan.Reset();
      evidence.Reset();
      planAvailable=false;
      reason="";
      if(!m_initialized)
         return(false);

      CHybridRuleSetupContext context;
      if(!m_adapter.Project(source,context,evidence))
        {
         reason=evidence.Reason;
         return(false);
        }

      const double score=Bounded(
         (source.HigherTrend.AITrendRegime+
          source.HigherTrend.AITrendMomentum+
          source.HigherTrend.AITrendSlope)/3.0);
      decision.Type=AI_DECISION_HOLD;
      decision.Action=AI_ACTION_HOLD;
      decision.Source=AI_SOURCE_BRAIN;
      decision.Symbol=source.Symbol;
      decision.Timeframe=source.EntryTimeframe;
      decision.Timestamp=source.ObservationTime;
      decision.Score=score;
      decision.Confidence=0.0;
      decision.Reason=evidence.Reason;
      decision.Valid=true;

      CTradeSetupCandidate candidate;
      if(!m_setupEngine.Build(context,candidate))
        {
         reason=candidate.Reason;
         decision.Reason=reason;
         return(true);
        }
      if(!m_planner.Build(candidate,plan))
        {
         reason=plan.Reason;
         decision.Reason=reason;
         return(true);
        }

      if(plan.Direction==TRADE_SETUP_BUY)
        {
         const double weakest=MathMin(source.HigherTrend.AITrendRegime,
            MathMin(source.HigherTrend.AITrendMomentum,
                    source.HigherTrend.AITrendSlope));
         decision.Type=AI_DECISION_BUY;
         decision.Action=AI_ACTION_BUY;
         decision.Confidence=Bounded(2.0*(weakest-50.0));
        }
      else if(plan.Direction==TRADE_SETUP_SELL)
        {
         const double weakest=MathMax(source.HigherTrend.AITrendRegime,
            MathMax(source.HigherTrend.AITrendMomentum,
                    source.HigherTrend.AITrendSlope));
         decision.Type=AI_DECISION_SELL;
         decision.Action=AI_ACTION_SELL;
         decision.Confidence=Bounded(2.0*(50.0-weakest));
        }
      else
         return(false);

      decision.EntryPrice=plan.EntryPrice;
      decision.StopLoss=plan.StopLossPrice;
      decision.TakeProfit=plan.TakeProfitPrice;
      decision.Reason="CR-013 tester-only objective structural Trade Plan";
      planAvailable=true;
      reason=plan.Reason;
      return(true);
     }

   void Shutdown()
     {
      m_initialized=false;
     }

   string ProviderId() const
     {
      return("OBJECTIVE_M15_M5_SETUP_TESTER_ONLY");
     }

   string ModelStatus() const
     {
      return("OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO");
     }

   bool ModelDeploymentAuthorized() const
     {
      return(false);
     }
  };

#endif
