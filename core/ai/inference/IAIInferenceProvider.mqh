//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : IAIInferenceProvider.mqh                               |
//| Layer   : Core / AI / Inference                                 |
//| Version : 1.1.0                                                  |
//| Purpose : Controlled AI inference provider boundary              |
//+------------------------------------------------------------------+

#ifndef CORE_AI_INFERENCE_IAIINFERENCEPROVIDER_MQH
#define CORE_AI_INFERENCE_IAIINFERENCEPROVIDER_MQH

#include "models/AIInferenceRequest.mqh"
#include "../models/AIDecision.mqh"

class IAIInferenceProvider
  {
public:
   virtual bool Initialize()
     {
      return(false);
     }

   virtual CAIDecision Evaluate(const CAIInferenceRequest &request)
     {
      CAIDecision decision;
      return(decision);
     }

   virtual void Shutdown()
     {
     }

   virtual string ProviderId() const
     {
     return("UNCONFIGURED_INFERENCE_PROVIDER");
     }

   virtual string ModelStatus() const
     {
      return("UNCONFIGURED_INFERENCE_PROVIDER_NO_GO");
     }

   virtual bool ModelDeploymentAuthorized() const
     {
      return(false);
     }
  };

#endif
