//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHybridRuleTradePlan.mq5                            |
//| Layer   : Tests / AI / Strategy                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Verify CR-013 setup and structural Trade Plan contract |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/strategy/HybridRuleSetupEngine.mqh"
#include "../core/ai/strategy/StructureAwareTradePlanner.mqh"

void BuildBaseContext(CHybridRuleSetupContext &context)
  {
   context.Reset();
   context.Symbol="XAUUSD";
   context.ExecutionTimeframe=PERIOD_M15;
   context.ClosedBarTime=D'2026.07.17 12:00';
   context.Direction=TRADE_SETUP_BUY;
   context.ClosedBarConfirmed=true;
   context.HigherTimeframeTrendAligned=true;
   context.PointOfInterestConfirmed=true;
   context.EntryTriggerConfirmed=true;
   context.EntryPrice=3000.0;
   context.StructuralStopPrice=2990.0;
   context.NearestStructuralTargetPrice=3030.0;
   context.Point=0.01;
   context.EstimatedCostPoints=2.0;
   context.MinimumRiskReward=2.0;
  }

int OnInit()
  {
   CHybridRuleSetupEngine setupEngine;
   CStructureAwareTradePlanner planner;

   CHybridRuleSetupContext buyContext;
   BuildBaseContext(buyContext);
   CTradeSetupCandidate buyCandidate;
   CStructureAwareTradePlan buyPlan;
   const bool buyValid=
      (setupEngine.Build(buyContext,buyCandidate) &&
       planner.Build(buyCandidate,buyPlan) &&
       buyPlan.Valid && buyPlan.Direction==TRADE_SETUP_BUY);
   const bool adaptiveRewardPreserved=
      (buyValid && buyPlan.RiskReward>2.9 &&
       MathAbs(buyPlan.RiskReward-2.0)>0.1 &&
       MathAbs(buyPlan.TakeProfitPrice-3030.0)<0.000001);

   CHybridRuleSetupContext sellContext;
   BuildBaseContext(sellContext);
   sellContext.Direction=TRADE_SETUP_SELL;
   sellContext.StructuralStopPrice=3012.0;
   sellContext.NearestStructuralTargetPrice=2960.0;
   CTradeSetupCandidate sellCandidate;
   CStructureAwareTradePlan sellPlan;
   const bool sellValid=
      (setupEngine.Build(sellContext,sellCandidate) &&
       planner.Build(sellCandidate,sellPlan) &&
       sellPlan.Valid && sellPlan.Direction==TRADE_SETUP_SELL &&
       sellPlan.RiskReward>3.3);

   CHybridRuleSetupContext missingPoi;
   BuildBaseContext(missingPoi);
   missingPoi.PointOfInterestConfirmed=false;
   CTradeSetupCandidate missingPoiCandidate;
   const bool missingPoiRejected=
      !setupEngine.Build(missingPoi,missingPoiCandidate);

   CHybridRuleSetupContext invalidGeometry;
   BuildBaseContext(invalidGeometry);
   invalidGeometry.StructuralStopPrice=3010.0;
   CTradeSetupCandidate invalidGeometryCandidate;
   const bool invalidGeometryRejected=
      !setupEngine.Build(invalidGeometry,invalidGeometryCandidate);

   CHybridRuleSetupContext openBar;
   BuildBaseContext(openBar);
   openBar.ClosedBarConfirmed=false;
   CTradeSetupCandidate openBarCandidate;
   const bool openBarRejected=
      !setupEngine.Build(openBar,openBarCandidate);

   CHybridRuleSetupContext insufficientReward;
   BuildBaseContext(insufficientReward);
   insufficientReward.NearestStructuralTargetPrice=3015.0;
   CTradeSetupCandidate insufficientCandidate;
   CStructureAwareTradePlan insufficientPlan;
   const bool insufficientRewardRejected=
      (setupEngine.Build(insufficientReward,insufficientCandidate) &&
       !planner.Build(insufficientCandidate,insufficientPlan) &&
       !insufficientPlan.Valid && insufficientPlan.RiskReward<2.0);

   const bool riskBoundaryPreserved=
      (buyPlan.Valid &&
       buyPlan.Reason==
       "Structure-aware Trade Plan accepted; Risk approval remains required.");

   const bool valid=(buyValid && sellValid && adaptiveRewardPreserved &&
                     missingPoiRejected && invalidGeometryRejected &&
                     openBarRejected && insufficientRewardRejected &&
                     riskBoundaryPreserved);

   Print("Hybrid BUY structural Trade Plan valid: ",buyValid);
   Print("Hybrid SELL structural Trade Plan valid: ",sellValid);
   Print("Hybrid adaptive RR above fixed 1:2 preserved: ",adaptiveRewardPreserved);
   Print("Hybrid missing POI rejected: ",missingPoiRejected);
   Print("Hybrid invalid structural geometry rejected: ",invalidGeometryRejected);
   Print("Hybrid open-bar setup rejected: ",openBarRejected);
   Print("Hybrid insufficient nearest-target RR rejected: ",insufficientRewardRejected);
   Print("Hybrid Trade Plan still requires Risk approval: ",riskBoundaryPreserved);
   Print("Hybrid Rule and Trade Plan contract valid: ",valid);

   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }

