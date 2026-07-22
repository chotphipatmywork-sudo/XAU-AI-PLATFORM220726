//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIEngine.mqh                                           |
//| Layer   : Engine                                                 |
//| Version : 4.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_ENGINE_AIENGINE_MQH
#define CORE_ENGINE_AIENGINE_MQH

#include "../brain/Brain.mqh"
#include "../ai/DecisionAdapter.mqh"
#include "../ai/DecisionExecutor.mqh"

#include "models/BrainPipelineResult.mqh"

class CAIEngine
{
private:

   CBrain              m_brain;
   CDecisionAdapter    m_adapter;
   CDecisionExecutor   m_executor;

public:

   //--------------------------------------------------

   bool Initialize()
   {
      return m_brain.Initialize();
   }

   //--------------------------------------------------

   bool Run(
   const string symbol,
   ENUM_TIMEFRAMES timeframe)
   {
      CBrainPipelineResult pipeline =
         m_brain.Think(symbol,timeframe);

      if(!pipeline.Valid)
         return false;

      CAIDecision decision =
         m_adapter.Convert(
            pipeline.Analysis);

      return
         m_executor.Execute(
            decision);
   }

   //--------------------------------------------------

   void Shutdown()
   {
      m_brain.Shutdown();
   }

};

#endif