//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AITrainingSample.mqh                                   |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Training input and independent target label            |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_AITRAININGSAMPLE_MQH
#define CORE_AI_MODELS_AITRAININGSAMPLE_MQH

#include "../features/FeatureExtractor.mqh"

class CAITrainingSample
  {
private:
   CAIFeatureVector m_features;
   double           m_label;

public:
   CAITrainingSample(void)
     {
      Reset();
     }

   void Reset(void)
     {
      m_features.Reset();
      m_label=0.0;
     }

   void SetFeatures(const CAIFeatureVector &features)
     {
      m_features=features;
     }

   void SetLabel(const double label)
     {
      m_label=label;
     }

   CAIFeatureVector Features(void) const
     {
      return(m_features);
     }

   double Label(void) const
     {
      return(m_label);
     }
  };

#endif
