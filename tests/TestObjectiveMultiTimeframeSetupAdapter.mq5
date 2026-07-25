//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestObjectiveMultiTimeframeSetupAdapter.mq5            |
//| Layer   : Tests / AI / Strategy                                  |
//| Version : 1.3.0                                                  |
//| Purpose : Verify CR-017 causal reversal-context setup contract   |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/strategy/ObjectiveMultiTimeframeSetupAdapter.mqh"
#include "../core/ai/strategy/HybridRuleSetupEngine.mqh"
#include "../core/ai/strategy/StructureAwareTradePlanner.mqh"

void BuildBuyInput(CObjectiveMultiTimeframeSetupInput &source)
  {
   source.Reset();
   source.Symbol="XAUUSD";
   source.HigherTimeframe=PERIOD_M15;
   source.EntryTimeframe=PERIOD_M5;
   source.ObservationTime=D'2026.07.17 12:00';
   source.HigherBarOpenTime=D'2026.07.17 11:45';
   source.ContextBarOpenTime=D'2026.07.17 11:50';
   source.EntryBarOpenTime=D'2026.07.17 11:55';
   source.HigherTrendKnownTime=source.ObservationTime;
   source.EntryStructureKnownTime=source.ObservationTime;

   source.HigherTrend.Valid=true;
   source.HigherTrend.Direction=TREND_BULLISH;
   source.HigherTrend.AITrendRegime=70.0;
   source.HigherTrend.AITrendMomentum=65.0;
   source.HigherTrend.AITrendSlope=60.0;

   source.EntryStructure.Valid=true;
   source.EntryStructure.LatestSwingHigh=3030.0;
   source.EntryStructure.LatestSwingLow=2995.0;

   source.ContextOpen=2995.6;
   source.ContextHigh=2995.8;
   source.ContextLow=2995.0;
   source.ContextClose=2995.2;
   source.EntryOpen=2995.2;
   source.EntryHigh=2996.2;
   source.EntryLow=2994.7;
   source.EntryClose=2995.8;
   source.EntryAtr=5.0;
   source.Point=0.01;
   source.EstimatedCostPoints=2.0;
   source.MinimumRiskReward=2.0;
  }

void BuildSellInput(CObjectiveMultiTimeframeSetupInput &source)
  {
   BuildBuyInput(source);
   source.HigherTrend.Direction=TREND_BEARISH;
   source.HigherTrend.AITrendRegime=30.0;
   source.HigherTrend.AITrendMomentum=35.0;
   source.HigherTrend.AITrendSlope=40.0;
   source.EntryStructure.LatestSwingHigh=3005.0;
   source.EntryStructure.LatestSwingLow=2960.0;
   source.ContextOpen=3004.4;
   source.ContextHigh=3004.9;
   source.ContextLow=3004.2;
   source.ContextClose=3004.8;
   source.EntryOpen=3004.8;
   source.EntryHigh=3005.3;
   source.EntryLow=3003.5;
   source.EntryClose=3004.2;
  }

int OnInit()
  {
   CObjectiveMultiTimeframeSetupAdapter adapter;
   CHybridRuleSetupEngine setupEngine;
   CStructureAwareTradePlanner planner;

   CObjectiveHybridSetupConfig config;
   const bool minimumReclaimConfigValid=
      (config.Valid() &&
       MathAbs(config.MinimumReclaimAtr-0.10)<0.000000001 &&
       adapter.SetConfig(config));

   CObjectiveMultiTimeframeSetupInput buyInput;
   BuildBuyInput(buyInput);
   CHybridRuleSetupContext buyContext;
   CObjectiveMultiTimeframeSetupEvidence buyEvidence;
   CTradeSetupCandidate buyCandidate;
   CStructureAwareTradePlan buyPlan;
   const bool buyValid=
      (adapter.Project(buyInput,buyContext,buyEvidence) &&
       buyEvidence.ValidObservation && buyEvidence.PoiConfirmed &&
       buyEvidence.TriggerConfirmed &&
       buyEvidence.ReversalContextConfirmed &&
       setupEngine.Build(buyContext,buyCandidate) &&
       planner.Build(buyCandidate,buyPlan) && buyPlan.Valid &&
       buyPlan.Direction==TRADE_SETUP_BUY && buyPlan.RiskReward>2.0);

   CObjectiveMultiTimeframeSetupInput sellInput;
   BuildSellInput(sellInput);
   CHybridRuleSetupContext sellContext;
   CObjectiveMultiTimeframeSetupEvidence sellEvidence;
   CTradeSetupCandidate sellCandidate;
   CStructureAwareTradePlan sellPlan;
   const bool sellValid=
      (adapter.Project(sellInput,sellContext,sellEvidence) &&
       sellEvidence.ValidObservation && sellEvidence.PoiConfirmed &&
       sellEvidence.TriggerConfirmed &&
       sellEvidence.ReversalContextConfirmed &&
       setupEngine.Build(sellContext,sellCandidate) &&
       planner.Build(sellCandidate,sellPlan) && sellPlan.Valid &&
       sellPlan.Direction==TRADE_SETUP_SELL && sellPlan.RiskReward>2.0);

   const bool objectiveEvidenceValid=
      (buyEvidence.SweepPenetrationAtr>0.0 &&
       buyEvidence.ReclaimDistanceAtr+0.000000001>=config.MinimumReclaimAtr &&
       buyEvidence.TriggerEngulfmentAtr>0.0 &&
       sellEvidence.SweepPenetrationAtr>0.0 &&
       sellEvidence.ReclaimDistanceAtr+0.000000001>=config.MinimumReclaimAtr &&
       sellEvidence.TriggerEngulfmentAtr>0.0);

   CObjectiveMultiTimeframeSetupInput weakReclaimInput;
   BuildBuyInput(weakReclaimInput);
   weakReclaimInput.EntryOpen=2995.10;
   weakReclaimInput.EntryHigh=2995.50;
   weakReclaimInput.EntryClose=2995.25;
   CHybridRuleSetupContext weakReclaimContext;
   CObjectiveMultiTimeframeSetupEvidence weakReclaimEvidence;
   CTradeSetupCandidate weakReclaimCandidate;
   const bool weakReclaimRejected=
      (adapter.Project(weakReclaimInput,weakReclaimContext,
                       weakReclaimEvidence) &&
       weakReclaimEvidence.ValidObservation &&
       weakReclaimEvidence.PoiConfirmed &&
       weakReclaimEvidence.SweepPenetrationAtr>0.0 &&
       weakReclaimEvidence.ReclaimDistanceAtr<config.MinimumReclaimAtr &&
       !weakReclaimEvidence.TriggerConfirmed &&
       !setupEngine.Build(weakReclaimContext,weakReclaimCandidate));

   CObjectiveMultiTimeframeSetupInput failedContextInput;
   BuildBuyInput(failedContextInput);
   failedContextInput.ContextOpen=2995.2;
   failedContextInput.ContextHigh=2995.7;
   failedContextInput.ContextLow=2995.0;
   failedContextInput.ContextClose=2995.5;
   CHybridRuleSetupContext failedContext;
   CObjectiveMultiTimeframeSetupEvidence failedContextEvidence;
   CTradeSetupCandidate failedContextCandidate;
   const bool failedContextRejected=
      (adapter.Project(failedContextInput,failedContext,
                       failedContextEvidence) &&
       failedContextEvidence.TriggerConfirmed &&
       !failedContextEvidence.ReversalContextConfirmed &&
       !setupEngine.Build(failedContext,failedContextCandidate));

   CObjectiveMultiTimeframeSetupInput noTriggerInput;
   BuildBuyInput(noTriggerInput);
   noTriggerInput.EntryOpen=2995.0;
   noTriggerInput.EntryHigh=2995.4;
   noTriggerInput.EntryLow=2994.95;
   noTriggerInput.EntryClose=2995.2;
   CHybridRuleSetupContext noTriggerContext;
   CObjectiveMultiTimeframeSetupEvidence noTriggerEvidence;
   CTradeSetupCandidate noTriggerCandidate;
   const bool noTriggerNonActionable=
      (adapter.Project(noTriggerInput,noTriggerContext,noTriggerEvidence) &&
       noTriggerEvidence.ValidObservation &&
       noTriggerEvidence.PoiConfirmed &&
       !noTriggerEvidence.TriggerConfirmed &&
       !setupEngine.Build(noTriggerContext,noTriggerCandidate));

   CObjectiveMultiTimeframeSetupInput futureInput;
   BuildBuyInput(futureInput);
   futureInput.EntryStructureKnownTime=futureInput.ObservationTime+300;
   CHybridRuleSetupContext futureContext;
   CObjectiveMultiTimeframeSetupEvidence futureEvidence;
   const bool futureRejected=
      !adapter.Project(futureInput,futureContext,futureEvidence);

   CObjectiveMultiTimeframeSetupInput formingInput;
   BuildBuyInput(formingInput);
   formingInput.EntryBarOpenTime=D'2026.07.17 11:58';
   CHybridRuleSetupContext formingContext;
   CObjectiveMultiTimeframeSetupEvidence formingEvidence;
   const bool formingRejected=
      !adapter.Project(formingInput,formingContext,formingEvidence);

   CObjectiveMultiTimeframeSetupInput insufficientInput;
   BuildBuyInput(insufficientInput);
   insufficientInput.EntryStructure.LatestSwingHigh=2998.0;
   CHybridRuleSetupContext insufficientContext;
   CObjectiveMultiTimeframeSetupEvidence insufficientEvidence;
   CTradeSetupCandidate insufficientCandidate;
   CStructureAwareTradePlan insufficientPlan;
   const bool insufficientRewardRejected=
      (adapter.Project(insufficientInput,insufficientContext,
                       insufficientEvidence) &&
       setupEngine.Build(insufficientContext,insufficientCandidate) &&
       !planner.Build(insufficientCandidate,insufficientPlan) &&
       !insufficientPlan.Valid && insufficientPlan.RiskReward<2.0);

   const bool timingRejected=(futureRejected && formingRejected);
   const bool riskBoundaryPreserved=
      (buyPlan.Valid &&
       buyPlan.Reason==
       "Structure-aware Trade Plan accepted; Risk approval remains required." &&
       buyEvidence.Reason==
       "Objective M15/M5 reversal-context evidence projected; Risk approval remains required.");

   const bool valid=(minimumReclaimConfigValid &&
                     buyValid && sellValid && objectiveEvidenceValid &&
                     weakReclaimRejected && failedContextRejected &&
                     noTriggerNonActionable && timingRejected &&
                     insufficientRewardRejected && riskBoundaryPreserved);

   Print("Objective M15/M5 BUY setup valid: ",buyValid);
   Print("Objective M15/M5 SELL setup valid: ",sellValid);
   Print("Objective minimum reclaim 0.10 ATR config valid: ",
         minimumReclaimConfigValid);
   Print("Objective sweep/reclaim evidence valid: ",objectiveEvidenceValid);
   Print("Objective sub-minimum reclaim rejected: ",weakReclaimRejected);
   Print("Objective failed M5 reversal context rejected: ",
         failedContextRejected);
   Print("Objective non-trigger remains non-actionable: ",noTriggerNonActionable);
   Print("Objective future/forming timing rejected: ",timingRejected);
   Print("Objective insufficient structural RR rejected: ",insufficientRewardRejected);
   Print("Objective Stage B Risk boundary preserved: ",riskBoundaryPreserved);
   Print("Objective M15/M5 Setup adapter contract valid: ",valid);

   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
