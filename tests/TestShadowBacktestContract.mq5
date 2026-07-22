//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowBacktestContract.mq5                         |
//| Layer   : Tests / Telemetry / Shadow                             |
//| Version : 1.1.0                                                  |
//| Purpose : Verify isolated Shadow backtest report safety contract |
//+------------------------------------------------------------------+

#property strict

#include "../core/telemetry/ShadowBacktestReportLogger.mqh"

input string BacktestContractFile="XAU_AI_SHADOW_BACKTEST_CONTRACT_TEST.csv";

bool Check(const bool condition,const string message)
  {
   if(!condition)
      Print("Shadow backtest contract failed: ",message);
   return(condition);
  }

int OnInit()
  {
   FileDelete(BacktestContractFile);

   CShadowBacktestReport report;
   report.StartTime=StringToTime("2026.07.01 00:00:00");
   report.EndTime=StringToTime("2026.07.02 00:00:00");
   report.FirstDecisionBar=StringToTime("2026.07.01 00:00:00");
   report.LastDecisionBar=StringToTime("2026.07.01 23:45:00");
   report.InferenceProvider="DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO";
   report.ModelStatus="DEVELOPMENT_HEURISTIC_MODEL_NO_GO";
   report.Decisions=96;
   report.RiskRejections=76;
   report.ShadowExecutions=20;
   report.ClosedTrades=20;
   report.WinningTrades=8;
   report.LosingTrades=11;
   report.BreakevenTrades=1;
   report.CumulativeProfitPoints=125.0;
   report.MaximumDrawdownPoints=1500.0;
   report.PaperPositionActive=false;
   report.ModelDeploymentAuthorized=false;
   report.LiveExecutionAuthorized=false;
   report.BrokerStateUnchanged=true;

   CShadowBacktestReportLogger logger;
   logger.SetFileName(BacktestContractFile);
   const bool written=logger.Write(report);
   const bool valid=report.SafetyValid();

   CShadowBacktestReport unsafeReport;
   unsafeReport.Decisions=1;
   unsafeReport.InferenceProvider="UNSAFE_PROVIDER";
   unsafeReport.ModelStatus="UNSAFE_MODEL";
   unsafeReport.BrokerStateUnchanged=false;
   const bool brokerMutationRejected=!unsafeReport.SafetyValid();

   CShadowBacktestReport unconfiguredReport;
   unconfiguredReport.Decisions=1;
   unconfiguredReport.InferenceProvider="UNCONFIGURED_INFERENCE_PROVIDER";
   unconfiguredReport.ModelStatus="UNCONFIGURED_INFERENCE_PROVIDER_NO_GO";
   unconfiguredReport.BrokerStateUnchanged=true;
   const bool unconfiguredRejected=!unconfiguredReport.SafetyValid();

   const bool passed=
      Check(report.CountsConsistent(),"trade counts") &&
      Check(valid,"safe report") &&
      Check(written && FileIsExist(BacktestContractFile),"report file") &&
      Check(brokerMutationRejected,"broker mutation rejection") &&
      Check(unconfiguredRejected,"unconfigured provider rejection");

   Print("Shadow backtest counts consistent: ",report.CountsConsistent());
   Print("Shadow backtest safe report valid: ",valid);
   Print("Shadow backtest broker mutation rejected: ",brokerMutationRejected);
   Print("Shadow backtest unconfigured provider rejected: ",unconfiguredRejected);
   Print("Shadow backtest contract valid: ",passed);
   FileDelete(BacktestContractFile);
   ExpertRemove();
   return(passed ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
