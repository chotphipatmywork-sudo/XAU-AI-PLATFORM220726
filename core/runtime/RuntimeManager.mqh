//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RuntimeManager.mqh                                     |
//| Layer   : Core / Runtime                                         |
//| Version : 5.8.0                                                  |
//| Purpose : Canonical Runtime with CR-017 causal reversal context  |
//+------------------------------------------------------------------+

#ifndef CORE_RUNTIME_RUNTIMEMANAGER_MQH
#define CORE_RUNTIME_RUNTIMEMANAGER_MQH


#include "../scheduler/EventLoop.mqh"

#include "../brain/Brain.mqh"

#include "../ai/BrainFeatureAdapter.mqh"
#include "../ai/inference/DevelopmentHeuristicInferenceProvider.mqh"
#include "../ai/inference/DirectionalResearchInferenceProvider.mqh"
#include "../ai/inference/SimpleTrendBaselineInferenceProvider.mqh"
#include "../ai/strategy/ObjectiveSetupResearchProvider.mqh"

#include "../decision/AIDecisionIntentAdapter.mqh"

#include "../risk/RiskManager.mqh"

#include "../execution/shadow/ShadowExecutionManager.mqh"
#include "../execution/models/ExecutionModeConfig.mqh"
#include "../telemetry/ShadowDecisionAuditLogger.mqh"
#include "../telemetry/ObjectiveSetupAuditLogger.mqh"
#include "models/ShadowRuntimeConfig.mqh"
#include "ClosedBarFreshnessGuard.mqh"
#include "StructureAwareExecutionPlanAdapter.mqh"



class CRuntimeManager : public ITickCallback
{

private:


   //--------------------------------------------------
   // Runtime Components
   //--------------------------------------------------

   CEventLoop m_eventLoop;


   CBrain m_brain;


   CBrainFeatureAdapter m_featureAdapter;

   CDevelopmentHeuristicInferenceProvider m_legacyInference;

   CDirectionalResearchInferenceProvider m_directionalInference;

   CSimpleTrendBaselineInferenceProvider m_simpleBaselineInference;

   CObjectiveSetupResearchProvider m_objectiveSetupInference;

   IAIInferenceProvider *m_inference;

   string m_inferenceProviderId;

   string m_inferenceModelStatus;

   CAIDecisionIntentAdapter m_decision;

   CRiskManager m_risk;


   CShadowExecutionManager m_shadowExecution;

   CExecutionModeConfig m_executionMode;

   CShadowDecisionAuditLogger m_decisionAudit;

   CObjectiveSetupAuditLogger m_objectiveSetupAudit;

   CStructureAwareExecutionPlanAdapter m_executionPlanAdapter;

   CClosedBarFreshnessGuard m_closedBarFreshness;



   //--------------------------------------------------

   bool m_running;


   string m_symbol;


   ENUM_TIMEFRAMES m_timeframe;

   datetime m_lastClosedBar;

   datetime m_firstDecisionBar;

   ulong m_decisions;

   ulong m_riskRejections;

   ulong m_shadowExecutions;

   string m_checkpointKey;

   bool m_usePersistentCheckpoint;

   int m_maximumMarketAgeSeconds;

   int m_maximumDecisionLagSeconds;

   bool m_objectiveSetupMode;

   double m_objectiveMinimumRiskReward;

   double m_simulatedSlippagePoints;



private:


   bool BuildObjectiveSetupSource(
      const CBrainPipelineResult &higherBrain,
      CObjectiveMultiTimeframeSetupInput &source)
   {
      source.Reset();
      if(!higherBrain.Valid || m_symbol=="" || m_timeframe!=PERIOD_M15 ||
         m_lastClosedBar<=0)
         return(false);

      const datetime observationTime=
         m_lastClosedBar+PeriodSeconds(PERIOD_M15);
      const datetime entryBarOpen=
         observationTime-PeriodSeconds(PERIOD_M5);
      const datetime contextBarOpen=
         entryBarOpen-PeriodSeconds(PERIOD_M5);
      const int entryShift=
         iBarShift(m_symbol,PERIOD_M5,entryBarOpen,true);
      const int contextShift=
         iBarShift(m_symbol,PERIOD_M5,contextBarOpen,true);
      if(entryShift<1 || contextShift<2 ||
         iTime(m_symbol,PERIOD_M5,entryShift)!=entryBarOpen ||
         iTime(m_symbol,PERIOD_M5,contextShift)!=contextBarOpen ||
         contextShift!=entryShift+1)
         return(false);

      CBrainPipelineResult entryBrain=
         m_brain.Think(m_symbol,PERIOD_M5,entryShift);
      if(!entryBrain.Valid)
         return(false);

      CConfirmedSwingStructureResult swingStructure;
      if(!m_brain.ConfirmedSwingStructure(
            m_symbol,PERIOD_M5,entryShift,entryBarOpen,
            observationTime,swingStructure))
         return(false);

      MqlTick tick;
      if(!SymbolInfoTick(m_symbol,tick))
         return(false);
      const double point=SymbolInfoDouble(m_symbol,SYMBOL_POINT);
      if(point<=0.0 || tick.ask<=0.0 || tick.bid<=0.0)
         return(false);

      source.Symbol=m_symbol;
      source.HigherTimeframe=PERIOD_M15;
      source.EntryTimeframe=PERIOD_M5;
      source.ObservationTime=observationTime;
      source.HigherBarOpenTime=m_lastClosedBar;
      source.ContextBarOpenTime=contextBarOpen;
      source.EntryBarOpenTime=entryBarOpen;
      source.HigherTrendKnownTime=observationTime;
      source.EntryStructureKnownTime=observationTime;
      source.SetHigherTrend(higherBrain.Analysis.Trend);
      source.SetEntryStructure(swingStructure);
      source.ContextOpen=iOpen(m_symbol,PERIOD_M5,contextShift);
      source.ContextHigh=iHigh(m_symbol,PERIOD_M5,contextShift);
      source.ContextLow=iLow(m_symbol,PERIOD_M5,contextShift);
      source.ContextClose=iClose(m_symbol,PERIOD_M5,contextShift);
      source.EntryOpen=iOpen(m_symbol,PERIOD_M5,entryShift);
      source.EntryHigh=iHigh(m_symbol,PERIOD_M5,entryShift);
      source.EntryLow=iLow(m_symbol,PERIOD_M5,entryShift);
      source.EntryClose=iClose(m_symbol,PERIOD_M5,entryShift);
      source.EntryAtr=entryBrain.Analysis.Volatility.ATR;
      source.Point=point;
      source.EstimatedCostPoints=
         MathMax(0.0,(tick.ask-tick.bid)/point)+
         m_simulatedSlippagePoints;
      source.MinimumRiskReward=m_objectiveMinimumRiskReward;
      return(true);
   }


   bool ProcessObjectiveAI(
      const CBrainPipelineResult &brainResult,
      const CAIInferenceRequest &request)
   {
      CObjectiveMultiTimeframeSetupInput source;
      if(!BuildObjectiveSetupSource(brainResult,source))
         return(false);

      CAIDecision decision;
      CStructureAwareTradePlan plan;
      CObjectiveMultiTimeframeSetupEvidence evidence;
      bool planAvailable=false;
      string setupReason="";
      if(!m_objectiveSetupInference.Evaluate(
            source,decision,plan,evidence,planAvailable,setupReason) ||
         !decision.Valid)
         return(false);

      CDecisionResult intent=m_decision.Convert(decision);
      if(!intent.Valid)
         return(false);
      if(m_decisions==0)
         m_firstDecisionBar=m_lastClosedBar;
      m_decisions++;

      CShadowRiskContext shadowRisk;
      shadowRisk.PaperPositionActive=m_shadowExecution.HasActivePosition();
      shadowRisk.DailyProfitPoints=m_shadowExecution.DailyProfitPoints();
      shadowRisk.DrawdownPoints=m_shadowExecution.DrawdownPoints();
      shadowRisk.MarketStale=m_shadowExecution.MarketStale(
         m_symbol,m_maximumMarketAgeSeconds);

      CRiskResult risk=m_risk.Evaluate(intent,shadowRisk);
      if(!risk.AllowTrade)
         m_riskRejections++;

      CExecutionResult result;
      if(risk.AllowTrade)
        {
         CExecutionPricePlan executionPlan;
         if(!planAvailable ||
            !m_executionPlanAdapter.Convert(plan,executionPlan))
           {
            result.Status=EXECUTION_REJECTED;
            result.Message=
               "Objective Shadow execution requires a valid structural Trade Plan.";
           }
         else
            result=m_shadowExecution.Execute(
               intent,risk,m_symbol,source.EntryTimeframe,executionPlan);
        }
      else
         result=m_shadowExecution.Execute(
            intent,risk,m_symbol,source.EntryTimeframe);

      m_decisionAudit.Write(
         m_lastClosedBar,
         m_symbol,
         m_timeframe,
         "4.0.0",
         m_objectiveSetupInference.ProviderId(),
         m_objectiveSetupInference.ModelStatus(),
         m_objectiveSetupInference.ModelDeploymentAuthorized(),
         request,
         iOpen(m_symbol,m_timeframe,1),
         iHigh(m_symbol,m_timeframe,1),
         iLow(m_symbol,m_timeframe,1),
         iClose(m_symbol,m_timeframe,1),
         brainResult.Analysis.Volatility.ATR,
         decision,
         intent,
         risk,
         result);

      m_objectiveSetupAudit.Write(
         source,evidence,plan,planAvailable,setupReason,
         decision,risk,result);

      if(!result.Success)
         return(false);

      m_shadowExecutions++;
      Print("Objective Shadow Runtime execution: ",result.Message,
            " | ticket=",result.Ticket,
            " | symbol=",m_symbol,
            " | observation=",TimeToString(
               source.ObservationTime,TIME_DATE|TIME_MINUTES));
      return(true);
   }


   //--------------------------------------------------
   // AI Processing
   //--------------------------------------------------

   bool ProcessAI(
      const CBrainPipelineResult &brainResult)
   {

      if(!brainResult.Valid)
         return false;



      CAIInferenceRequest request;
      if(!m_featureAdapter.Extract(brainResult.Analysis,request.Features))
         return false;

      request.LegacyTrendScore =
         brainResult.Analysis.Trend.Strength;


      request.LegacyVolatilityScore =
         brainResult.Analysis.Volatility.ExpansionScore;


      request.LegacyLiquidityScore =
         brainResult.Analysis.Liquidity.Score;


      request.LegacySessionScore =
         brainResult.Analysis.Session.Confidence;

      if(m_objectiveSetupMode)
         return(ProcessObjectiveAI(brainResult,request));



      //--------------------------------------------------
      // AI Decision
      //--------------------------------------------------

      CAIDecision decision =
         m_inference.Evaluate(request);



      if(!decision.Valid)
         return false;

      CDecisionResult intent=m_decision.Convert(decision);
      if(!intent.Valid)
         return false;
      if(m_decisions==0)
         m_firstDecisionBar=m_lastClosedBar;
      m_decisions++;

      CShadowRiskContext shadowRisk;
      shadowRisk.PaperPositionActive=m_shadowExecution.HasActivePosition();
      shadowRisk.DailyProfitPoints=m_shadowExecution.DailyProfitPoints();
      shadowRisk.DrawdownPoints=m_shadowExecution.DrawdownPoints();
      shadowRisk.MarketStale=m_shadowExecution.MarketStale(
         m_symbol,
         m_maximumMarketAgeSeconds);

      CRiskResult risk=m_risk.Evaluate(intent,shadowRisk);
      if(!risk.AllowTrade)
         m_riskRejections++;

      CExecutionResult result=
         m_shadowExecution.Execute(
            intent,
            risk,
            m_symbol,
            m_timeframe);

      m_decisionAudit.Write(
         m_lastClosedBar,
         m_symbol,
         m_timeframe,
         "4.0.0",
         m_inference.ProviderId(),
         m_inference.ModelStatus(),
         m_inference.ModelDeploymentAuthorized(),
         request,
         iOpen(m_symbol,m_timeframe,1),
         iHigh(m_symbol,m_timeframe,1),
         iLow(m_symbol,m_timeframe,1),
         iClose(m_symbol,m_timeframe,1),
         brainResult.Analysis.Volatility.ATR,
         decision,
         intent,
         risk,
         result);


      if(!result.Success)
         return false;

      m_shadowExecutions++;
      Print("Shadow Runtime execution: ",result.Message,
            " | ticket=",result.Ticket,
            " | symbol=",m_symbol,
            " | closed_bar=",TimeToString(m_lastClosedBar,TIME_DATE|TIME_MINUTES));


      return true;

   }



   //--------------------------------------------------
   // Runtime Pipeline
   //--------------------------------------------------

   void ProcessPipeline()
   {

      if(m_symbol == "")
         return;

      m_shadowExecution.Update(m_symbol);

      const datetime closedBar=iTime(m_symbol,m_timeframe,1);
      if(closedBar<=0 || closedBar==m_lastClosedBar)
         return;
      if(m_checkpointKey!="")
        {
         const double sharedLast=GlobalVariableGet(m_checkpointKey);
         if((datetime)sharedLast>=closedBar)
           {
            m_lastClosedBar=(datetime)sharedLast;
            return;
           }
         if(!GlobalVariableSetOnCondition(
               m_checkpointKey,
               (double)closedBar,
               sharedLast))
           {
            m_lastClosedBar=(datetime)GlobalVariableGet(m_checkpointKey);
            return;
           }
        }
      m_lastClosedBar=closedBar;

      if(!m_closedBarFreshness.IsFresh(
            closedBar,
            m_timeframe,
            TimeCurrent(),
            m_maximumDecisionLagSeconds))
        {
         Print("Shadow Runtime skipped stale closed bar: ",
               TimeToString(closedBar,TIME_DATE|TIME_MINUTES));
         return;
        }


      CBrainPipelineResult result =
         m_brain.Think(
            m_symbol,
            m_timeframe,
            1);



      ProcessAI(result);

   }



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CRuntimeManager()
   {

      m_running = false;

      m_symbol = "";

      m_timeframe = PERIOD_CURRENT;

      m_lastClosedBar = 0;

      m_firstDecisionBar = 0;

      m_decisions = 0;

      m_riskRejections = 0;

      m_shadowExecutions = 0;

      m_checkpointKey = "";

      m_usePersistentCheckpoint = true;

      m_maximumMarketAgeSeconds = 120;

      m_maximumDecisionLagSeconds = 120;

      m_objectiveSetupMode = false;

      m_objectiveMinimumRiskReward = 2.0;

      m_simulatedSlippagePoints = 2.0;

      m_inference = NULL;

      m_inferenceProviderId = "UNCONFIGURED_INFERENCE_PROVIDER";

      m_inferenceModelStatus = "UNCONFIGURED_INFERENCE_PROVIDER_NO_GO";

   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {
      CShadowRuntimeConfig config;
      return Initialize(config);
   }

   bool Initialize(const CShadowRuntimeConfig &config)
   {

      if(!config.Valid())
         return false;

      const bool testerMode=(bool)MQLInfoInteger(MQL_TESTER);
      if(!config.InferenceProviderAllowed(testerMode))
        {
         Print("Shadow Runtime rejected inference provider outside Strategy Tester.");
         return false;
        }

      if(!m_eventLoop.Initialize())
         return false;



      m_eventLoop.SetTickCallback(
         GetPointer(this));



      if(!m_brain.Initialize())
         return false;



      m_objectiveSetupMode=
         (config.InferenceProvider==SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP);
      if(m_objectiveSetupMode)
        {
         m_inference=NULL;
         if(!m_objectiveSetupInference.Initialize())
            return false;
         m_inferenceProviderId=m_objectiveSetupInference.ProviderId();
         m_inferenceModelStatus=m_objectiveSetupInference.ModelStatus();
        }
      else
        {
         if(config.InferenceProvider==SHADOW_INFERENCE_DIRECTIONAL_RESEARCH)
            m_inference=GetPointer(m_directionalInference);
         else if(config.InferenceProvider==SHADOW_INFERENCE_SIMPLE_TREND_BASELINE)
            m_inference=GetPointer(m_simpleBaselineInference);
         else
            m_inference=GetPointer(m_legacyInference);

         if(m_inference==NULL || !m_inference.Initialize())
            return false;

         m_inferenceProviderId=m_inference.ProviderId();
         m_inferenceModelStatus=m_inference.ModelStatus();
        }



      m_executionMode.Reset();
      if(!m_executionMode.IsShadow() || !m_executionMode.IsLiveLocked())
         return false;
      m_risk.SetShadowLossLimits(
         config.MaximumDailyLossPoints,
         config.MaximumDrawdownPoints);
      m_maximumMarketAgeSeconds=config.MaximumMarketAgeSeconds;
      m_maximumDecisionLagSeconds=config.MaximumDecisionLagSeconds;
      m_objectiveMinimumRiskReward=config.ObjectiveMinimumRiskReward;
      m_simulatedSlippagePoints=config.Execution.SimulatedSlippagePoints;
      m_usePersistentCheckpoint=config.UsePersistentCheckpoint;
      m_decisionAudit.SetFileName(config.DecisionAuditFile);
      m_objectiveSetupAudit.SetFileName(config.ObjectiveSetupAuditFile);
      if(!m_shadowExecution.Initialize(config.Execution))
         return false;



      m_running = true;


      return true;

   }



   //--------------------------------------------------
   // Set Context
   //--------------------------------------------------

   void SetContext(
      const string symbol,
      ENUM_TIMEFRAMES timeframe)
   {

      if(symbol==m_symbol && timeframe==m_timeframe)
         return;

      m_symbol = symbol;
      m_timeframe = timeframe;
      m_lastClosedBar=0;
      if(m_usePersistentCheckpoint)
        {
         m_checkpointKey=StringFormat(
            "XAUAI_SHADOW_%I64d_%s_%d",
            AccountInfoInteger(ACCOUNT_LOGIN),
            symbol,
            (int)timeframe);
         if(!GlobalVariableCheck(m_checkpointKey))
            GlobalVariableSet(m_checkpointKey,0.0);
         m_lastClosedBar=(datetime)GlobalVariableGet(m_checkpointKey);
        }
      else
        {
         m_checkpointKey="";
         m_lastClosedBar=iTime(symbol,timeframe,1);
        }

   }



   //--------------------------------------------------
   // External Tick
   //--------------------------------------------------

   void OnTick()
   {

      if(!m_running)
         return;


      m_eventLoop.OnTick();

   }



   //--------------------------------------------------
   // Tick Callback
   //--------------------------------------------------

   void OnTickEvent()
   {

      ProcessPipeline();

   }



   //--------------------------------------------------
   // Timer
   //--------------------------------------------------

   void OnTimer()
   {

      if(!m_running)
         return;


      m_eventLoop.OnTimer();

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

      if(!m_running)
         return;


      m_shadowExecution.Shutdown();

      if(m_inference!=NULL)
        {
         m_inference.Shutdown();
         m_inference=NULL;
        }

      if(m_objectiveSetupMode)
        {
         m_objectiveSetupInference.Shutdown();
         m_objectiveSetupMode=false;
        }


      m_brain.Shutdown();


      m_eventLoop.Shutdown();


      m_running = false;

   }



   //--------------------------------------------------
   // Status
   //--------------------------------------------------

   bool IsRunning() const
   {
      return m_running;
   }

   ulong DecisionCount() const
   {
      return m_decisions;
   }

   ulong RiskRejectionCount() const
   {
      return m_riskRejections;
   }

   ulong ShadowExecutionCount() const
   {
      return m_shadowExecutions;
   }

   bool HasShadowPosition() const
   {
      return m_shadowExecution.HasActivePosition();
   }

   datetime LastClosedBar() const
   {
      return m_lastClosedBar;
   }

   datetime FirstDecisionBar() const
   {
      return m_firstDecisionBar;
   }

   string Symbol() const
   {
      return m_symbol;
   }

   ENUM_TIMEFRAMES Timeframe() const
   {
      return m_timeframe;
   }

   bool EmergencyStopEnabled() const
   {
      return m_risk.EmergencyStopEnabled();
   }

   bool ModelDeploymentAuthorized() const
   {
      if(m_objectiveSetupMode)
         return(m_executionMode.ModelDeploymentAuthorized &&
                m_objectiveSetupInference.ModelDeploymentAuthorized());
      return(m_executionMode.ModelDeploymentAuthorized &&
             m_inference!=NULL &&
             m_inference.ModelDeploymentAuthorized());
   }

   string InferenceProviderId() const
   {
      return(m_inferenceProviderId);
   }

   string InferenceModelStatus() const
   {
      return(m_inferenceModelStatus);
   }

   bool LiveExecutionAuthorized() const
   {
      return m_executionMode.LiveExecutionAuthorized;
   }

   CShadowTrade ShadowSnapshot() const
   {
      return m_shadowExecution.Snapshot();
   }

   double ShadowDailyProfitPoints() const
   {
      return m_shadowExecution.DailyProfitPoints();
   }

   double ShadowCumulativeProfitPoints() const
   {
      return m_shadowExecution.CumulativeProfitPoints();
   }

   double ShadowDrawdownPoints() const
   {
      return m_shadowExecution.DrawdownPoints();
   }

   double ShadowMaximumDrawdownPoints() const
   {
      return m_shadowExecution.MaximumDrawdownPoints();
   }

   ulong ShadowClosedTradeCount() const
   {
      return m_shadowExecution.ClosedTradeCount();
   }

   ulong ShadowWinningTradeCount() const
   {
      return m_shadowExecution.WinningTradeCount();
   }

   ulong ShadowLosingTradeCount() const
   {
      return m_shadowExecution.LosingTradeCount();
   }

   ulong ShadowBreakevenTradeCount() const
   {
      return m_shadowExecution.BreakevenTradeCount();
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_risk.SetEmergencyStop(enabled);
      m_shadowExecution.SetEmergencyStop(enabled);
   }


};


#endif

//+------------------------------------------------------------------+
