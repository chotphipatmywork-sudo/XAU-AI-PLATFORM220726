//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowStructuralExecutionSafety.mq5               |
//| Layer   : Tests / Execution / Shadow                             |
//| Version : 1.0.0                                                  |
//| Purpose : Prove Risk-gated structural paper execution safety     |
//+------------------------------------------------------------------+

#property strict

#include "../core/execution/shadow/ShadowExecutionEngine.mqh"

input string StructuralAuditFile="XAU_AI_STRUCTURAL_EXECUTION_TEST_AUDIT.csv";
input string StructuralStateFile="XAU_AI_STRUCTURAL_EXECUTION_TEST_STATE.csv";

void BuildBuyPricePlan(CExecutionPricePlan &plan)
  {
   plan.Reset();
   plan.Direction=DECISION_BUY;
   plan.ReferenceEntryPrice=2000.0;
   plan.StopLossPrice=1999.0;
   plan.TakeProfitPrice=2003.0;
   plan.EstimatedCostPoints=2.0;
   plan.MinimumRiskReward=2.0;
   plan.Source="SYNTHETIC_STRUCTURAL_TEST";
   plan.Valid=true;
  }

int OnInit()
  {
   const int positionsBefore=PositionsTotal();
   const int ordersBefore=OrdersTotal();
   FileDelete(StructuralAuditFile);
   FileDelete(StructuralStateFile);

   CShadowExecutionConfig config;
   config.AuditFile=StructuralAuditFile;
   config.StateFile=StructuralStateFile;
   config.DefaultVolume=0.01;
   config.StopLossPoints=100.0;
   config.TakeProfitPoints=200.0;
   config.SimulatedSlippagePoints=2.0;

   CShadowExecutionEngine engine;
   if(!engine.Initialize(config))
      return(INIT_FAILED);

   CExecutionContext context;
   context.Symbol="XAUUSD";
   context.Timeframe=PERIOD_M5;
   context.Ask=2000.20;
   context.Bid=2000.00;
   context.Point=0.01;
   context.CurrentTime=D'2026.07.18 12:00';
   context.Decision.Valid=true;
   context.Decision.Decision=DECISION_BUY;
   context.Decision.Confidence=75.0;

   CExecutionPricePlan validPlan;
   BuildBuyPricePlan(validPlan);
   CRiskResult rejectedRisk;
   rejectedRisk.Reject("Synthetic Risk rejection.");
   CExecutionResult rejected=engine.Execute(context,rejectedRisk,validPlan);
   const bool rejectedRiskValid=(!rejected.Success && !engine.HasActivePosition());

   CRiskResult approvedRisk;
   approvedRisk.Accept("Synthetic Risk approval.");
   approvedRisk.Score=100.0;

   CExecutionPricePlan mismatchPlan;
   BuildBuyPricePlan(mismatchPlan);
   mismatchPlan.Direction=DECISION_SELL;
   CExecutionResult mismatch=engine.Execute(context,approvedRisk,mismatchPlan);
   const bool mismatchRejected=(!mismatch.Success && !engine.HasActivePosition());

   CExecutionPricePlan lowRewardPlan;
   BuildBuyPricePlan(lowRewardPlan);
   lowRewardPlan.TakeProfitPrice=2002.0;
   CExecutionResult lowReward=engine.Execute(context,approvedRisk,lowRewardPlan);
   const bool lowRewardRejected=(!lowReward.Success && !engine.HasActivePosition());

   CExecutionResult opened=engine.Execute(context,approvedRisk,validPlan);
   const bool exactPrices=
      (opened.Success &&
       MathAbs(opened.StopLoss-validPlan.StopLossPrice)<0.000001 &&
       MathAbs(opened.TakeProfit-validPlan.TakeProfitPrice)<0.000001);
   CExecutionResult duplicate=engine.Execute(context,approvedRisk,validPlan);
   const bool duplicateRejected=!duplicate.Success;

   const bool lifecycle=
      (engine.Update(2003.10,2003.30,0.01,D'2026.07.18 12:15') &&
       !engine.HasActivePosition());
   engine.SetEmergencyStop(true);
   CExecutionResult emergency=engine.Execute(context,approvedRisk,validPlan);
   const bool emergencyRejected=!emergency.Success;
   const bool brokerUnchanged=(PositionsTotal()==positionsBefore &&
                               OrdersTotal()==ordersBefore);
   const bool valid=(rejectedRiskValid && mismatchRejected &&
                     lowRewardRejected && exactPrices && duplicateRejected &&
                     lifecycle && emergencyRejected && brokerUnchanged);

   Print("Structural execution rejected Risk valid: ",rejectedRiskValid);
   Print("Structural execution direction mismatch rejected: ",mismatchRejected);
   Print("Structural execution sub-minimum RR rejected: ",lowRewardRejected);
   Print("Structural execution supplied Stop/Target preserved: ",exactPrices);
   Print("Structural execution duplicate protection valid: ",duplicateRejected);
   Print("Structural execution paper lifecycle valid: ",lifecycle);
   Print("Structural execution emergency stop valid: ",emergencyRejected);
   Print("Structural execution broker state unchanged: ",brokerUnchanged);
   Print("Structural execution safety contract valid: ",valid);

   FileDelete(StructuralStateFile);
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
