//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowTelemetryLogger.mqh                              |
//| Layer   : Core / Telemetry                                       |
//| Version : 1.1.0                                                  |
//| Purpose : Periodic Shadow health CSV and Expert heartbeat        |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_SHADOWTELEMETRYLOGGER_MQH
#define CORE_TELEMETRY_SHADOWTELEMETRYLOGGER_MQH

#include "models/ShadowTelemetrySnapshot.mqh"

class CShadowTelemetryLogger
  {
private:
   string   m_fileName;
   datetime m_lastWrite;
   int      m_intervalSeconds;

public:
   CShadowTelemetryLogger()
     {
      m_fileName="XAU_AI_SHADOW_TELEMETRY.csv";
      m_lastWrite=0;
      m_intervalSeconds=60;
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool LogIfDue(const CShadowTelemetrySnapshot &snapshot)
     {
      if(snapshot.Timestamp<=0)
         return(false);
      if(m_lastWrite>0 &&
         snapshot.Timestamp-m_lastWrite<m_intervalSeconds)
         return(false);

      const int handle=FileOpen(m_fileName,
                                FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ,
                                ',');
      if(handle==INVALID_HANDLE)
         return(false);
      if(FileSize(handle)==0)
         FileWrite(handle,
                   "timestamp","symbol","timeframe","last_closed_bar","running",
                   "model_deployment_authorized","live_execution_authorized",
                   "emergency_stop","decisions","risk_rejections",
                   "shadow_executions","paper_position_active",
                   "daily_profit_points","cumulative_profit_points",
                   "drawdown_points");
      FileSeek(handle,0,SEEK_END);
      FileWrite(handle,
                TimeToString(snapshot.Timestamp,TIME_DATE|TIME_SECONDS),
                snapshot.Symbol,
                EnumToString(snapshot.Timeframe),
                TimeToString(snapshot.LastClosedBar,TIME_DATE|TIME_MINUTES),
                snapshot.Running ? "true" : "false",
                snapshot.ModelDeploymentAuthorized ? "true" : "false",
                snapshot.LiveExecutionAuthorized ? "true" : "false",
                snapshot.EmergencyStop ? "true" : "false",
                (long)snapshot.Decisions,
                (long)snapshot.RiskRejections,
                (long)snapshot.ShadowExecutions,
                snapshot.PaperPositionActive ? "true" : "false",
                snapshot.DailyProfitPoints,
                snapshot.CumulativeProfitPoints,
                snapshot.DrawdownPoints);
      FileFlush(handle);
      FileClose(handle);
      m_lastWrite=snapshot.Timestamp;

      Print("Shadow heartbeat | symbol=",snapshot.Symbol,
            " | decisions=",snapshot.Decisions,
            " | risk_rejections=",snapshot.RiskRejections,
            " | executions=",snapshot.ShadowExecutions,
            " | active=",snapshot.PaperPositionActive,
            " | daily_points=",DoubleToString(snapshot.DailyProfitPoints,1),
            " | live_authorized=false");
      return(true);
     }
  };

#endif
