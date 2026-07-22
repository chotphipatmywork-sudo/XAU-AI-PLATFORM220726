//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowBacktestReportLogger.mqh                         |
//| Layer   : Core / Telemetry                                       |
//| Version : 1.1.0                                                  |
//| Purpose : Write one canonical Shadow Strategy Tester summary     |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_SHADOWBACKTESTREPORTLOGGER_MQH
#define CORE_TELEMETRY_SHADOWBACKTESTREPORTLOGGER_MQH

#include "models/ShadowBacktestReport.mqh"

class CShadowBacktestReportLogger
  {
private:
   string m_fileName;

public:
   CShadowBacktestReportLogger()
     {
      m_fileName="XAU_AI_SHADOW_BACKTEST_REPORT.csv";
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool Write(const CShadowBacktestReport &report)
     {
      const int handle=FileOpen(m_fileName,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
      if(handle==INVALID_HANDLE)
         return(false);
      FileWrite(handle,
                "start_time","end_time","first_decision_bar","last_decision_bar",
                "inference_provider","model_status","decisions","risk_rejections","shadow_executions",
                "closed_trades","winning_trades","losing_trades","breakeven_trades",
                "cumulative_profit_points","maximum_drawdown_points",
                "paper_position_active","model_deployment_authorized",
                "live_execution_authorized","broker_state_unchanged",
                "counts_consistent","safety_valid");
      FileWrite(handle,
                TimeToString(report.StartTime,TIME_DATE|TIME_SECONDS),
                TimeToString(report.EndTime,TIME_DATE|TIME_SECONDS),
                TimeToString(report.FirstDecisionBar,TIME_DATE|TIME_MINUTES),
                TimeToString(report.LastDecisionBar,TIME_DATE|TIME_MINUTES),
                report.InferenceProvider,
                report.ModelStatus,
                (long)report.Decisions,
                (long)report.RiskRejections,
                (long)report.ShadowExecutions,
                (long)report.ClosedTrades,
                (long)report.WinningTrades,
                (long)report.LosingTrades,
                (long)report.BreakevenTrades,
                report.CumulativeProfitPoints,
                report.MaximumDrawdownPoints,
                report.PaperPositionActive ? "true" : "false",
                report.ModelDeploymentAuthorized ? "true" : "false",
                report.LiveExecutionAuthorized ? "true" : "false",
                report.BrokerStateUnchanged ? "true" : "false",
                report.CountsConsistent() ? "true" : "false",
                report.SafetyValid() ? "true" : "false");
      FileFlush(handle);
      FileClose(handle);
      return(true);
     }
  };

#endif
