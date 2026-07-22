//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowExecutionConfig.mqh                              |
//| Layer   : Core / Execution / Shadow                             |
//| Version : 1.1.0                                                  |
//| Purpose : Bounded paper-execution configuration                  |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_SHADOWEXECUTIONCONFIG_MQH
#define CORE_EXECUTION_SHADOW_SHADOWEXECUTIONCONFIG_MQH

class CShadowExecutionConfig
  {
public:
   double DefaultVolume;
   double StopLossPoints;
   double TakeProfitPoints;
   double SimulatedSlippagePoints;
   int    MaximumHoldingBars;
   bool   OnePositionOnly;
   int    StateCheckpointSeconds;
   string AuditFile;
   string StateFile;

   CShadowExecutionConfig()
     {
      DefaultVolume=0.01;
      StopLossPoints=500.0;
      TakeProfitPoints=1000.0;
      SimulatedSlippagePoints=2.0;
      MaximumHoldingBars=64;
      OnePositionOnly=true;
      StateCheckpointSeconds=60;
      AuditFile="XAU_AI_SHADOW_AUDIT.csv";
      StateFile="XAU_AI_SHADOW_STATE.csv";
     }

   bool Valid() const
     {
      return(DefaultVolume>0.0 &&
             StopLossPoints>0.0 &&
             TakeProfitPoints>0.0 &&
             SimulatedSlippagePoints>=0.0 &&
             MaximumHoldingBars>0 &&
             StateCheckpointSeconds>0 &&
             AuditFile!="" &&
             StateFile!="");
     }
  };

#endif
