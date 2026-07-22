//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowInferenceProviderMode.mqh                        |
//| Layer   : Core / AI / Inference / Models                        |
//| Version : 1.2.0                                                  |
//| Purpose : Safe selectable Shadow inference provider modes        |
//+------------------------------------------------------------------+

#ifndef CORE_AI_INFERENCE_MODELS_SHADOWINFERENCEPROVIDERMODE_MQH
#define CORE_AI_INFERENCE_MODELS_SHADOWINFERENCEPROVIDERMODE_MQH

enum ENUM_SHADOW_INFERENCE_PROVIDER
  {
   SHADOW_INFERENCE_LEGACY_LOCKED=0,
   SHADOW_INFERENCE_DIRECTIONAL_RESEARCH=1,
   SHADOW_INFERENCE_SIMPLE_TREND_BASELINE=2,
   SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP=3
  };

#endif
