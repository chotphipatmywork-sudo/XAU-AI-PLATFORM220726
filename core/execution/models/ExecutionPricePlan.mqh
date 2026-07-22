//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionPricePlan.mqh                                |
//| Layer   : Core / Execution / Models                             |
//| Version : 1.0.0                                                  |
//| Purpose : Execution-owned absolute paper price-plan contract     |
//+------------------------------------------------------------------+

#ifndef XAU_EXECUTION_PRICE_PLAN_MQH
#define XAU_EXECUTION_PRICE_PLAN_MQH

#include "../../decision/models/DecisionResult.mqh"

class CExecutionPricePlan
  {
public:
   ENUM_DECISION Direction;
   double        ReferenceEntryPrice;
   double        StopLossPrice;
   double        TakeProfitPrice;
   double        EstimatedCostPoints;
   double        MinimumRiskReward;
   string        Source;
   bool          Valid;

   CExecutionPricePlan()
     {
      Reset();
     }

   void Reset()
     {
      Direction=DECISION_NONE;
      ReferenceEntryPrice=0.0;
      StopLossPrice=0.0;
      TakeProfitPrice=0.0;
      EstimatedCostPoints=0.0;
      MinimumRiskReward=0.0;
      Source="";
      Valid=false;
     }

   bool ContractValid() const
     {
      return(Valid &&
             (Direction==DECISION_BUY || Direction==DECISION_SELL) &&
             MathIsValidNumber(ReferenceEntryPrice) &&
             MathIsValidNumber(StopLossPrice) &&
             MathIsValidNumber(TakeProfitPrice) &&
             MathIsValidNumber(EstimatedCostPoints) &&
             MathIsValidNumber(MinimumRiskReward) &&
             ReferenceEntryPrice>0.0 && StopLossPrice>0.0 &&
             TakeProfitPrice>0.0 && EstimatedCostPoints>=0.0 &&
             MinimumRiskReward>0.0 && Source!="");
     }
  };

#endif
