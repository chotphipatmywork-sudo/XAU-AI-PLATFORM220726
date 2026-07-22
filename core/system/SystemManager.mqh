//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SystemManager.mqh                                      |
//| Layer   : System                                                 |
//| Version : 5.3.0                                                  |
//| Purpose : System Runtime Coordinator                             |
//+------------------------------------------------------------------+

#ifndef CORE_SYSTEM_SYSTEMMANAGER_MQH
#define CORE_SYSTEM_SYSTEMMANAGER_MQH

#include "../runtime/RuntimeManager.mqh"
#include "../telemetry/TelemetryManager.mqh"
#include "../telemetry/ShadowTelemetryLogger.mqh"
#include "../runtime/models/ShadowRuntimeConfig.mqh"
#include "../telemetry/models/ShadowBacktestReport.mqh"

class CSystemManager
{
private:

   CRuntimeManager     m_runtime;
   CTelemetryManager   m_telemetry;
   CShadowTelemetryLogger m_shadowTelemetry;

   bool                m_ready;

public:

   CSystemManager()
   {
      m_ready = false;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      CShadowRuntimeConfig config;
      return Initialize(config);
   }

   bool Initialize(const CShadowRuntimeConfig &config)
   {
      if(!m_runtime.Initialize(config))
         return false;

      m_telemetry.Reset();
      m_shadowTelemetry.SetFileName(config.TelemetryFile);

      m_ready = true;

      return true;
   }

   //--------------------------------------------------

   bool Update(
      const string symbol,
      ENUM_TIMEFRAMES timeframe)
   {
      if(!m_ready)
         return false;

      m_telemetry.OnTick();

      m_runtime.SetContext(
         symbol,
         timeframe);

      m_runtime.OnTick();

      return true;
   }

   //--------------------------------------------------

   void OnTimer()
   {
      if(!m_ready)
         return;

      m_runtime.OnTimer();

      CShadowTelemetrySnapshot snapshot;
      snapshot.Timestamp=TimeCurrent();
      snapshot.Symbol=m_runtime.Symbol();
      snapshot.Timeframe=m_runtime.Timeframe();
      snapshot.LastClosedBar=m_runtime.LastClosedBar();
      snapshot.Running=m_runtime.IsRunning();
      snapshot.ModelDeploymentAuthorized=m_runtime.ModelDeploymentAuthorized();
      snapshot.LiveExecutionAuthorized=m_runtime.LiveExecutionAuthorized();
      snapshot.EmergencyStop=m_runtime.EmergencyStopEnabled();
      snapshot.Decisions=m_runtime.DecisionCount();
      snapshot.RiskRejections=m_runtime.RiskRejectionCount();
      snapshot.ShadowExecutions=m_runtime.ShadowExecutionCount();
      snapshot.PaperPositionActive=m_runtime.HasShadowPosition();
      snapshot.DailyProfitPoints=m_runtime.ShadowDailyProfitPoints();
      snapshot.CumulativeProfitPoints=m_runtime.ShadowCumulativeProfitPoints();
      snapshot.DrawdownPoints=m_runtime.ShadowDrawdownPoints();
      m_shadowTelemetry.LogIfDue(snapshot);
   }

   //--------------------------------------------------

   void Shutdown()
   {
      if(!m_ready)
         return;

      m_runtime.Shutdown();

      m_ready = false;
   }

   //--------------------------------------------------

   bool IsReady() const
   {
      return m_ready;
   }

   //--------------------------------------------------

   CTelemetryManager* Telemetry()
   {
      return &m_telemetry;
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_runtime.SetEmergencyStop(enabled);
   }

   void CaptureShadowBacktestReport(CShadowBacktestReport &report,
                                    const datetime startTime,
                                    const datetime endTime,
                                    const bool brokerStateUnchanged) const
   {
      report.Reset();
      report.StartTime=startTime;
      report.EndTime=endTime;
      report.FirstDecisionBar=m_runtime.FirstDecisionBar();
      report.LastDecisionBar=m_runtime.LastClosedBar();
      report.InferenceProvider=m_runtime.InferenceProviderId();
      report.ModelStatus=m_runtime.InferenceModelStatus();
      report.Decisions=m_runtime.DecisionCount();
      report.RiskRejections=m_runtime.RiskRejectionCount();
      report.ShadowExecutions=m_runtime.ShadowExecutionCount();
      report.ClosedTrades=m_runtime.ShadowClosedTradeCount();
      report.WinningTrades=m_runtime.ShadowWinningTradeCount();
      report.LosingTrades=m_runtime.ShadowLosingTradeCount();
      report.BreakevenTrades=m_runtime.ShadowBreakevenTradeCount();
      report.CumulativeProfitPoints=m_runtime.ShadowCumulativeProfitPoints();
      report.MaximumDrawdownPoints=m_runtime.ShadowMaximumDrawdownPoints();
      report.PaperPositionActive=m_runtime.HasShadowPosition();
      report.ModelDeploymentAuthorized=m_runtime.ModelDeploymentAuthorized();
      report.LiveExecutionAuthorized=m_runtime.LiveExecutionAuthorized();
      report.BrokerStateUnchanged=brokerStateUnchanged;
   }

};

#endif
