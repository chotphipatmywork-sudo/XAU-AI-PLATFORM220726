//+------------------------------------------------------------------+
//|                                                XAU-AI-PLATFORM   |
//|                         Copyright 2026                           |
//+------------------------------------------------------------------+

#property strict
#property version "2.80"

#include "core/kernel/Kernel.mqh"
#include "core/telemetry/ShadowBacktestReportLogger.mqh"

input bool ShadowEmergencyStop=false;
input double ShadowVolume=0.01;
input double ShadowStopLossPoints=500.0;
input double ShadowTakeProfitPoints=1000.0;
input double ShadowSlippagePoints=2.0;
input int ShadowMaximumHoldingBars=64;
input double ShadowMaximumDailyLossPoints=2000.0;
input double ShadowMaximumDrawdownPoints=3000.0;
input int ShadowMaximumMarketAgeSeconds=120;
input int ShadowMaximumDecisionLagSeconds=120;
input ENUM_SHADOW_INFERENCE_PROVIDER ShadowInferenceProvider=
   SHADOW_INFERENCE_LEGACY_LOCKED;
input double ObjectiveMinimumRiskReward=2.0;

//--------------------------------------------------
// Main Kernel
//--------------------------------------------------

CKernel Kernel;
bool BacktestMode=false;
bool KernelStopped=false;
int BrokerPositionsBefore=0;
int BrokerOrdersBefore=0;
datetime BacktestStartTime=0;
string BacktestReportFile="XAU_AI_SHADOW_BACKTEST_REPORT.csv";

//+------------------------------------------------------------------+
//| Expert initialization                                            |
//+------------------------------------------------------------------+

int OnInit()
{
   BacktestMode=(bool)MQLInfoInteger(MQL_TESTER);
   KernelStopped=false;
   BrokerPositionsBefore=PositionsTotal();
   BrokerOrdersBefore=OrdersTotal();
   BacktestStartTime=TimeCurrent();

   CShadowRuntimeConfig config;
   config.Execution.DefaultVolume=ShadowVolume;
   config.Execution.StopLossPoints=ShadowStopLossPoints;
   config.Execution.TakeProfitPoints=ShadowTakeProfitPoints;
   config.Execution.SimulatedSlippagePoints=ShadowSlippagePoints;
   config.Execution.MaximumHoldingBars=ShadowMaximumHoldingBars;
   config.MaximumDailyLossPoints=ShadowMaximumDailyLossPoints;
   config.MaximumDrawdownPoints=ShadowMaximumDrawdownPoints;
   config.MaximumMarketAgeSeconds=ShadowMaximumMarketAgeSeconds;
   config.MaximumDecisionLagSeconds=ShadowMaximumDecisionLagSeconds;
   config.InferenceProvider=ShadowInferenceProvider;
   config.ObjectiveMinimumRiskReward=ObjectiveMinimumRiskReward;

   if(ShadowInferenceProvider==SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP &&
      (!BacktestMode || _Period!=PERIOD_M15))
     {
      Print("Objective M15/M5 Setup provider requires Strategy Tester on M15.");
      return(INIT_FAILED);
     }

   if(BacktestMode)
     {
      if(ShadowInferenceProvider==SHADOW_INFERENCE_DIRECTIONAL_RESEARCH)
        {
         config.Execution.AuditFile="XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_AUDIT.csv";
         config.Execution.StateFile="XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_STATE.csv";
         config.DecisionAuditFile="XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_DECISIONS_V4.csv";
         config.TelemetryFile="XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_TELEMETRY.csv";
         BacktestReportFile="XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_REPORT.csv";
        }
      else if(ShadowInferenceProvider==SHADOW_INFERENCE_SIMPLE_TREND_BASELINE)
        {
         config.Execution.AuditFile="XAU_AI_SHADOW_BACKTEST_SIMPLE_BASELINE_AUDIT.csv";
         config.Execution.StateFile="XAU_AI_SHADOW_BACKTEST_SIMPLE_BASELINE_STATE.csv";
         config.DecisionAuditFile="XAU_AI_SHADOW_BACKTEST_SIMPLE_BASELINE_DECISIONS_V4.csv";
         config.TelemetryFile="XAU_AI_SHADOW_BACKTEST_SIMPLE_BASELINE_TELEMETRY.csv";
         BacktestReportFile="XAU_AI_SHADOW_BACKTEST_SIMPLE_BASELINE_REPORT.csv";
        }
      else if(ShadowInferenceProvider==SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP)
        {
         config.Execution.AuditFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_EXECUTION_AUDIT.csv";
         config.Execution.StateFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_STATE.csv";
         config.DecisionAuditFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv";
         config.TelemetryFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_TELEMETRY.csv";
         config.ObjectiveSetupAuditFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv";
         BacktestReportFile="XAU_AI_SHADOW_BACKTEST_OBJECTIVE_REPORT.csv";
        }
      else
        {
         config.Execution.AuditFile="XAU_AI_SHADOW_BACKTEST_AUDIT.csv";
         config.Execution.StateFile="XAU_AI_SHADOW_BACKTEST_STATE.csv";
         config.DecisionAuditFile="XAU_AI_SHADOW_BACKTEST_DECISIONS_V4.csv";
         config.TelemetryFile="XAU_AI_SHADOW_BACKTEST_TELEMETRY.csv";
         BacktestReportFile="XAU_AI_SHADOW_BACKTEST_REPORT.csv";
        }
      config.UsePersistentCheckpoint=false;
      config.Execution.StateCheckpointSeconds=900;
      FileDelete(config.Execution.AuditFile);
      FileDelete(config.Execution.StateFile);
      FileDelete(config.DecisionAuditFile);
      FileDelete(config.TelemetryFile);
      FileDelete(config.ObjectiveSetupAuditFile);
      FileDelete(BacktestReportFile);
     }

   if(!Kernel.Initialize(config))
   {
      Print("Kernel initialization failed.");
      return INIT_FAILED;
   }

   Kernel.SetEmergencyStop(ShadowEmergencyStop);

   EventSetTimer(1);

   Print("XAU AI PLATFORM Shadow Runtime Started.");
   Print("Model deployment authorized: false");
   Print("Live execution authorized: false");
   Print("Shadow emergency stop: ",ShadowEmergencyStop);
   Print("Shadow volume: ",DoubleToString(ShadowVolume,2));
   Print("Shadow SL/TP points: ",ShadowStopLossPoints,"/",ShadowTakeProfitPoints);
   Print("Shadow maximum holding bars: ",ShadowMaximumHoldingBars);
   Print("Shadow daily loss/drawdown points: ",
         ShadowMaximumDailyLossPoints,"/",ShadowMaximumDrawdownPoints);
   Print("Shadow maximum decision lag seconds: ",
         ShadowMaximumDecisionLagSeconds);
   Print("Strategy Tester mode: ",BacktestMode);
   Print("Shadow inference provider mode: ",EnumToString(ShadowInferenceProvider));
   Print("Objective minimum structural RR: ",ObjectiveMinimumRiskReward);
   if(BacktestMode)
      Print("Shadow backtest artifacts use isolated BACKTEST file names.");

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Tick                                                      |
//+------------------------------------------------------------------+

void OnTick()
{
   Kernel.Tick(
      _Symbol,
      _Period
   );
}

//+------------------------------------------------------------------+
//| Expert Timer                                                     |
//+------------------------------------------------------------------+

void OnTimer()
{
   Kernel.OnTimer();
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+

void OnDeinit(const int reason)
{
   EventKillTimer();

   if(!KernelStopped)
     {
      Kernel.Shutdown();
      KernelStopped=true;
     }

   Print("XAU AI PLATFORM Stopped.");
}

//+------------------------------------------------------------------+
//| Strategy Tester summary                                          |
//+------------------------------------------------------------------+

double OnTester()
  {
   if(!BacktestMode)
      return(0.0);

   Kernel.Shutdown();
   KernelStopped=true;

   const bool brokerStateUnchanged=(PositionsTotal()==BrokerPositionsBefore &&
                                    OrdersTotal()==BrokerOrdersBefore);
   CShadowBacktestReport report;
   Kernel.CaptureShadowBacktestReport(
      report,BacktestStartTime,TimeCurrent(),brokerStateUnchanged);

   CShadowBacktestReportLogger logger;
   logger.SetFileName(BacktestReportFile);
   const bool reportWritten=logger.Write(report);

   Print("Shadow backtest decisions/risk rejections/executions: ",
         report.Decisions,"/",report.RiskRejections,"/",report.ShadowExecutions);
   Print("Shadow backtest closed/win/loss/breakeven: ",
         report.ClosedTrades,"/",report.WinningTrades,"/",
         report.LosingTrades,"/",report.BreakevenTrades);
   Print("Shadow backtest cumulative/max drawdown points: ",
         report.CumulativeProfitPoints,"/",report.MaximumDrawdownPoints);
   Print("Shadow backtest broker state unchanged: ",report.BrokerStateUnchanged);
   Print("Shadow backtest report written: ",reportWritten);
   Print("Shadow backtest safety valid: ",report.SafetyValid());
   Print("Shadow backtest inference provider: ",report.InferenceProvider);
   Print("Shadow backtest model status: ",report.ModelStatus);
   Print("Shadow backtest deployment authorized: false");

   return(report.SafetyValid() && reportWritten ? 1.0 : 0.0);
  }
//+------------------------------------------------------------------+
