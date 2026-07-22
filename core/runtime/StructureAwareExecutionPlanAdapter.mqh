//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureAwareExecutionPlanAdapter.mqh                |
//| Layer   : Core / Runtime / Boundary Adapters                    |
//| Version : 1.0.0                                                  |
//| Purpose : Map Risk-gated AI Trade Plan to Execution ownership    |
//+------------------------------------------------------------------+

#ifndef XAU_STRUCTURE_EXECUTION_ADAPTER_MQH
#define XAU_STRUCTURE_EXECUTION_ADAPTER_MQH

#include "../ai/strategy/models/StructureAwareTradePlan.mqh"
#include "../execution/models/ExecutionPricePlan.mqh"

class CStructureAwareExecutionPlanAdapter
  {
public:
   bool Convert(const CStructureAwareTradePlan &source,
                CExecutionPricePlan &target) const
     {
      target.Reset();
      if(!source.Valid)
         return(false);

      if(source.Direction==TRADE_SETUP_BUY)
         target.Direction=DECISION_BUY;
      else if(source.Direction==TRADE_SETUP_SELL)
         target.Direction=DECISION_SELL;
      else
         return(false);

      target.ReferenceEntryPrice=source.EntryPrice;
      target.StopLossPrice=source.StopLossPrice;
      target.TakeProfitPrice=source.TakeProfitPrice;
      target.EstimatedCostPoints=source.EstimatedCostPoints;
      target.MinimumRiskReward=source.MinimumRiskReward;
      target.Source="CR-013_OBJECTIVE_M15_M5_STRUCTURAL_PLAN";
      target.Valid=true;
      if(!target.ContractValid())
        {
         target.Reset();
         return(false);
        }
      return(true);
     }
  };

#endif
