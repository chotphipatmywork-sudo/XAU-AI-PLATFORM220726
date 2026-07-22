//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : AILearningManager.mqh                                  |
//| Layer   : Core / AI                                              |
//| Version : 1.0.0                                                  |
//| Purpose : AI Learning Manager                                    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_AILEARNINGMANAGER_MQH
#define CORE_AI_AILEARNINGMANAGER_MQH

#include "AITrainingEngine.mqh"
#include "AIInferenceEngine.mqh"

//--------------------------------------------------
// AI Learning Manager
//--------------------------------------------------

class CAILearningManager
{

private:

   CAITrainingEngine  m_training;
   CAIInferenceEngine m_inference;

   bool m_initialized;

public:

   //--------------------------------------------------

   CAILearningManager()
   {
      m_initialized = false;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      if(!m_training.Initialize())
         return false;

      if(!m_inference.Initialize())
         return false;

      m_initialized = true;

      return true;
   }

   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }

   //--------------------------------------------------

   bool Train()
   {
      if(!m_initialized)
         return false;

      return m_training.Train();
   }

   //--------------------------------------------------

   bool Predict(
      CAIDecision &decision)
   {
      if(!m_initialized)
         return false;

      return m_inference.Predict(decision);
   }

   //--------------------------------------------------

   CAITrainingEngine* TrainingEngine()
   {
      return &m_training;
   }

   //--------------------------------------------------

   CAIInferenceEngine* InferenceEngine()
   {
      return &m_inference;
   }

};

#endif