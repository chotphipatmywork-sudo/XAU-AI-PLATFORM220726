//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowBacktestReport.mqh                               |
//| Layer   : Core / Telemetry / Models                              |
//| Version : 1.2.0                                                  |
//| Purpose : End-to-end Shadow Strategy Tester evidence             |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_MODELS_SHADOWBACKTESTREPORT_MQH
#define CORE_TELEMETRY_MODELS_SHADOWBACKTESTREPORT_MQH

class CShadowBacktestReport
  {
public:
   datetime StartTime;
   datetime EndTime;
   datetime FirstDecisionBar;
   datetime LastDecisionBar;
   string   InferenceProvider;
   string   ModelStatus;
   ulong    Decisions;
   ulong    RiskRejections;
   ulong    ShadowExecutions;
   ulong    ClosedTrades;
   ulong    WinningTrades;
   ulong    LosingTrades;
   ulong    BreakevenTrades;
   double   CumulativeProfitPoints;
   double   MaximumDrawdownPoints;
   bool     PaperPositionActive;
   bool     ModelDeploymentAuthorized;
   bool     LiveExecutionAuthorized;
   bool     BrokerStateUnchanged;

   CShadowBacktestReport()
     {
      Reset();
     }

   void Reset()
     {
      StartTime=0;
      EndTime=0;
      FirstDecisionBar=0;
      LastDecisionBar=0;
      InferenceProvider="";
      ModelStatus="";
      Decisions=0;
      RiskRejections=0;
      ShadowExecutions=0;
      ClosedTrades=0;
      WinningTrades=0;
      LosingTrades=0;
      BreakevenTrades=0;
      CumulativeProfitPoints=0.0;
      MaximumDrawdownPoints=0.0;
      PaperPositionActive=false;
      ModelDeploymentAuthorized=false;
      LiveExecutionAuthorized=false;
      BrokerStateUnchanged=false;
     }

   bool CountsConsistent() const
     {
      return(ClosedTrades==WinningTrades+LosingTrades+BreakevenTrades &&
             ShadowExecutions>=ClosedTrades &&
             Decisions>=ShadowExecutions);
     }

   bool SafetyValid() const
     {
      return(Decisions>0 &&
             InferenceProvider!="" &&
             StringFind(InferenceProvider,"UNCONFIGURED")<0 &&
             StringFind(ModelStatus,"NO_GO")>=0 &&
             StringFind(ModelStatus,"UNCONFIGURED")<0 &&
             CountsConsistent() &&
             !ModelDeploymentAuthorized &&
             !LiveExecutionAuthorized &&
             BrokerStateUnchanged);
     }
  };

#endif
