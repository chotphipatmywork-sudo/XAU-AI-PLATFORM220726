//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowTelemetrySnapshot.mqh                            |
//| Layer   : Core / Telemetry / Models                              |
//| Version : 1.0.0                                                  |
//| Purpose : Operational Shadow Runtime health snapshot             |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_MODELS_SHADOWTELEMETRYSNAPSHOT_MQH
#define CORE_TELEMETRY_MODELS_SHADOWTELEMETRYSNAPSHOT_MQH

class CShadowTelemetrySnapshot
  {
public:
   datetime        Timestamp;
   string          Symbol;
   ENUM_TIMEFRAMES Timeframe;
   datetime        LastClosedBar;
   bool            Running;
   bool            ModelDeploymentAuthorized;
   bool            LiveExecutionAuthorized;
   bool            EmergencyStop;
   ulong           Decisions;
   ulong           RiskRejections;
   ulong           ShadowExecutions;
   bool            PaperPositionActive;
   double          DailyProfitPoints;
   double          CumulativeProfitPoints;
   double          DrawdownPoints;

   CShadowTelemetrySnapshot()
     {
      Timestamp=0;
      Symbol="";
      Timeframe=PERIOD_CURRENT;
      LastClosedBar=0;
      Running=false;
      ModelDeploymentAuthorized=false;
      LiveExecutionAuthorized=false;
      EmergencyStop=false;
      Decisions=0;
      RiskRejections=0;
      ShadowExecutions=0;
      PaperPositionActive=false;
      DailyProfitPoints=0.0;
      CumulativeProfitPoints=0.0;
      DrawdownPoints=0.0;
     }
  };

#endif
