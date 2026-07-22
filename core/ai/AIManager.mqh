//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : AIManager.mqh                                          |
//| Layer   : Core / AI                                              |
//| Version : 5.0.0                                                  |
//| Purpose : AI Decision Manager                                    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_AIMANAGER_MQH
#define CORE_AI_AIMANAGER_MQH

#include "AIDecisionEngine.mqh"
#include "models/AIDecision.mqh"

//--------------------------------------------------
// AI Manager
//--------------------------------------------------

class CAIManager
{
private:

   CAIDecisionEngine m_engine;

   bool m_initialized;

public:

   //--------------------------------------------------

   CAIManager()
   {
      m_initialized = false;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      m_initialized = true;

      return true;
   }

   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }

   //--------------------------------------------------
   // Evaluate AI Decision
   //--------------------------------------------------

   CAIDecision Evaluate(
      const double trendScore,
      const double volatilityScore,
      const double liquidityScore,
      const double sessionScore)
   {
      CAIDecision decision;

      if(!m_initialized)
         return decision;

      return m_engine.Evaluate(
         trendScore,
         volatilityScore,
         liquidityScore,
         sessionScore);
   }

   //--------------------------------------------------

   void Shutdown()
   {
      m_initialized = false;
   }

};

#endif