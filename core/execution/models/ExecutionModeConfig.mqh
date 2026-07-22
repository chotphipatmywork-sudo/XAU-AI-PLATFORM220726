//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionModeConfig.mqh                                |
//| Layer   : Core / Execution / Models                              |
//| Version : 1.0.0                                                  |
//| Purpose : Safe-default execution mode and deployment lock        |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_MODELS_EXECUTIONMODECONFIG_MQH
#define CORE_EXECUTION_MODELS_EXECUTIONMODECONFIG_MQH

enum ENUM_PLATFORM_EXECUTION_MODE
  {
   EXECUTION_MODE_SHADOW=0,
   EXECUTION_MODE_LIVE_LOCKED
  };

class CExecutionModeConfig
  {
public:
   ENUM_PLATFORM_EXECUTION_MODE Mode;
   bool                         ModelDeploymentAuthorized;
   bool                         LiveExecutionAuthorized;

   CExecutionModeConfig()
     {
      Reset();
     }

   void Reset()
     {
      Mode=EXECUTION_MODE_SHADOW;
      ModelDeploymentAuthorized=false;
      LiveExecutionAuthorized=false;
     }

   bool IsShadow() const
     {
      return(Mode==EXECUTION_MODE_SHADOW);
     }

   bool IsLiveLocked() const
     {
      return(Mode==EXECUTION_MODE_LIVE_LOCKED ||
             !ModelDeploymentAuthorized ||
             !LiveExecutionAuthorized);
     }
  };

#endif
