//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DevelopmentHeuristicInferenceProvider.mqh              |
//| Layer   : Core / AI / Inference                                 |
//| Version : 1.1.0                                                  |
//| Purpose : Locked compatibility provider for legacy AI heuristic  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_INFERENCE_DEVELOPMENTHEURISTICINFERENCEPROVIDER_MQH
#define CORE_AI_INFERENCE_DEVELOPMENTHEURISTICINFERENCEPROVIDER_MQH

#include "IAIInferenceProvider.mqh"
#include "../AIManager.mqh"

class CDevelopmentHeuristicInferenceProvider : public IAIInferenceProvider
  {
private:
   CAIManager m_ai;

public:
   virtual bool Initialize()
     {
      return(m_ai.Initialize());
     }

   virtual CAIDecision Evaluate(const CAIInferenceRequest &request)
     {
      CAIDecision decision;
      if(!request.FeatureSchemaValid())
         return(decision);
      return(m_ai.Evaluate(request.LegacyTrendScore,
                           request.LegacyVolatilityScore,
                           request.LegacyLiquidityScore,
                           request.LegacySessionScore));
     }

   virtual void Shutdown()
     {
      m_ai.Shutdown();
     }

   virtual string ProviderId() const
     {
      return("DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO");
     }

   virtual string ModelStatus() const
     {
      return("DEVELOPMENT_HEURISTIC_MODEL_NO_GO");
     }

   virtual bool ModelDeploymentAuthorized() const
     {
      return(false);
     }
  };

#endif
