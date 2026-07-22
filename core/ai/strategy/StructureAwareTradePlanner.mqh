//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureAwareTradePlanner.mqh                         |
//| Layer   : Core / AI / Strategy                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Validate conservative structure-aware trade geometry  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STRATEGY_STRUCTUREAWARETRADEPLANNER_MQH
#define CORE_AI_STRATEGY_STRUCTUREAWARETRADEPLANNER_MQH

#include "models/TradeSetupCandidate.mqh"
#include "models/StructureAwareTradePlan.mqh"

class CStructureAwareTradePlanner
  {
private:
   bool Reject(CStructureAwareTradePlan &plan,
               const string reason) const
     {
      plan.Valid=false;
      plan.Reason=reason;
      return(false);
     }

public:
   bool Build(const CTradeSetupCandidate &candidate,
              CStructureAwareTradePlan &plan) const
     {
      plan.Reset();

      if(!candidate.Valid)
         return(Reject(plan,"Trade Plan requires a valid Setup Candidate."));

      if(candidate.Point<=0.0 || candidate.MinimumRiskReward<=0.0 ||
         candidate.EstimatedCostPoints<0.0)
         return(Reject(plan,"Trade Plan received invalid planning values."));

      const double grossRiskPoints=
         MathAbs(candidate.EntryPrice-candidate.StructuralStopPrice)/candidate.Point;
      const double grossRewardPoints=
         MathAbs(candidate.NearestStructuralTargetPrice-candidate.EntryPrice)/candidate.Point;
      const double effectiveRiskPoints=
         grossRiskPoints+candidate.EstimatedCostPoints;
      const double netRewardPoints=
         grossRewardPoints-candidate.EstimatedCostPoints;

      plan.Symbol=candidate.Symbol;
      plan.ExecutionTimeframe=candidate.ExecutionTimeframe;
      plan.ClosedBarTime=candidate.ClosedBarTime;
      plan.Direction=candidate.Direction;
      plan.EntryPrice=candidate.EntryPrice;
      plan.StopLossPrice=candidate.StructuralStopPrice;
      plan.TakeProfitPrice=candidate.NearestStructuralTargetPrice;
      plan.GrossRiskPoints=grossRiskPoints;
      plan.GrossRewardPoints=grossRewardPoints;
      plan.EstimatedCostPoints=candidate.EstimatedCostPoints;
      plan.EffectiveRiskPoints=effectiveRiskPoints;
      plan.NetRewardPoints=netRewardPoints;
      plan.MinimumRiskReward=candidate.MinimumRiskReward;

      if(!MathIsValidNumber(effectiveRiskPoints) ||
         !MathIsValidNumber(netRewardPoints) ||
         effectiveRiskPoints<=0.0 || netRewardPoints<=0.0)
         return(Reject(plan,"Trade Plan has no positive cost-adjusted reward."));

      plan.RiskReward=netRewardPoints/effectiveRiskPoints;
      if(!MathIsValidNumber(plan.RiskReward) ||
         plan.RiskReward+0.000000001<candidate.MinimumRiskReward)
         return(Reject(plan,"Trade Plan rejected: nearest structural Target is below minimum RR."));

      plan.Reason="Structure-aware Trade Plan accepted; Risk approval remains required.";
      plan.Valid=true;
      return(true);
     }
  };

#endif

