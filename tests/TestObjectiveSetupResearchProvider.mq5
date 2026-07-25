//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestObjectiveSetupResearchProvider.mq5                |
//| Layer   : Tests / AI / Strategy                                  |
//| Version : 1.2.0                                                  |
//| Purpose : Verify tester-only CR-017 provider contract            |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/strategy/ObjectiveSetupResearchProvider.mqh"
#include "../core/runtime/StructureAwareExecutionPlanAdapter.mqh"
#include "../core/runtime/RuntimeManager.mqh"

void BuildObjectiveBuySource(CObjectiveMultiTimeframeSetupInput &source)
  {
   source.Reset();
   source.Symbol="XAUUSD";
   source.HigherTimeframe=PERIOD_M15;
   source.EntryTimeframe=PERIOD_M5;
   source.ObservationTime=D'2026.07.18 12:00';
   source.HigherBarOpenTime=D'2026.07.18 11:45';
   source.ContextBarOpenTime=D'2026.07.18 11:50';
   source.EntryBarOpenTime=D'2026.07.18 11:55';
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

void BuildObjectiveSellSource(CObjectiveMultiTimeframeSetupInput &source)
  {
   BuildObjectiveBuySource(source);
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

bool EvaluateSource(CObjectiveSetupResearchProvider &provider,
                    const CObjectiveMultiTimeframeSetupInput &source,
                    CAIDecision &decision,
                    CStructureAwareTradePlan &plan,
                    bool &available)
  {
   CObjectiveMultiTimeframeSetupEvidence evidence;
   string reason="";
   return(provider.Evaluate(
      source,decision,plan,evidence,available,reason));
  }

int OnInit()
  {
   CShadowRuntimeConfig config;
   config.InferenceProvider=SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP;
   const bool forwardBlocked=!config.InferenceProviderAllowed(false);
   const bool testerAllowed=config.InferenceProviderAllowed(true);
   CRuntimeManager runtime;
   const bool runtimeForwardBlocked=!runtime.Initialize(config);
   if(runtime.IsRunning())
      runtime.Shutdown();

   CObjectiveSetupResearchProvider provider;
   if(!provider.Initialize())
      return(INIT_FAILED);

   CObjectiveMultiTimeframeSetupInput buySource;
   BuildObjectiveBuySource(buySource);
   CAIDecision buyDecision;
   CStructureAwareTradePlan buyPlan;
   bool buyAvailable=false;
   const bool buyValid=
      (EvaluateSource(provider,buySource,buyDecision,buyPlan,buyAvailable) &&
       buyDecision.Valid && buyDecision.Action==AI_ACTION_BUY &&
       buyAvailable && buyPlan.Valid && buyPlan.RiskReward>2.0);

   CObjectiveMultiTimeframeSetupInput sellSource;
   BuildObjectiveSellSource(sellSource);
   CAIDecision sellDecision;
   CStructureAwareTradePlan sellPlan;
   bool sellAvailable=false;
   const bool sellValid=
      (EvaluateSource(provider,sellSource,sellDecision,sellPlan,sellAvailable) &&
       sellDecision.Valid && sellDecision.Action==AI_ACTION_SELL &&
       sellAvailable && sellPlan.Valid && sellPlan.RiskReward>2.0);

   CObjectiveMultiTimeframeSetupInput holdSource;
   BuildObjectiveBuySource(holdSource);
   holdSource.EntryOpen=2995.0;
   holdSource.EntryHigh=2995.4;
   holdSource.EntryLow=2994.95;
   holdSource.EntryClose=2995.2;
   CAIDecision holdDecision;
   CStructureAwareTradePlan holdPlan;
   bool holdAvailable=true;
   const bool holdValid=
      (EvaluateSource(provider,holdSource,holdDecision,holdPlan,holdAvailable) &&
       holdDecision.Valid && holdDecision.Action==AI_ACTION_HOLD &&
       !holdAvailable && !holdPlan.Valid);

   CStructureAwareExecutionPlanAdapter boundaryAdapter;
   CExecutionPricePlan executionPlan;
   const bool boundaryValid=
      (boundaryAdapter.Convert(buyPlan,executionPlan) &&
       executionPlan.ContractValid() &&
       executionPlan.Direction==DECISION_BUY &&
       MathAbs(executionPlan.StopLossPrice-buyPlan.StopLossPrice)<0.000001 &&
       MathAbs(executionPlan.TakeProfitPrice-buyPlan.TakeProfitPrice)<0.000001);

   const bool identity=
      (provider.ProviderId()=="OBJECTIVE_M15_M5_SETUP_TESTER_ONLY");
   const bool noGo=
      (provider.ModelStatus()=="OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO" &&
       !provider.ModelDeploymentAuthorized());
   const bool valid=(forwardBlocked && testerAllowed && runtimeForwardBlocked &&
                     buyValid && sellValid && holdValid && boundaryValid &&
                     identity && noGo);

   Print("Objective Setup Forward blocked: ",forwardBlocked);
   Print("Objective Setup Strategy Tester allowed: ",testerAllowed);
   Print("Objective Setup Runtime Forward initialization blocked: ",runtimeForwardBlocked);
   Print("Objective Setup BUY structural plan valid: ",buyValid);
   Print("Objective Setup SELL structural plan valid: ",sellValid);
   Print("Objective Setup incomplete trigger HOLD valid: ",holdValid);
   Print("Objective Setup Execution boundary mapping valid: ",boundaryValid);
   Print("Objective Setup provider identity valid: ",identity);
   Print("Objective Setup deployment NO-GO lock valid: ",noGo);
   Print("Objective Setup research provider contract valid: ",valid);

   provider.Shutdown();
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
