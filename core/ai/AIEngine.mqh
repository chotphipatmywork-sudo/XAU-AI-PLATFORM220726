//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIEngine.mqh                                           |
//| Layer   : Core / AI                                              |
//| Version : 3.0.0                                                  |
//| Purpose : AI Runtime Facade                                      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_AIENGINE_MQH
#define CORE_AI_AIENGINE_MQH

#include "AIManager.mqh"
#include "models/AIDecision.mqh"


//--------------------------------------------------
// AI Engine
//--------------------------------------------------

class CAIEngine
{

private:

   CAIManager m_manager;

   bool m_initialized;


public:


   //--------------------------------------------------

   CAIEngine()
   {
      m_initialized = false;
   }



   //--------------------------------------------------

   bool Initialize()
   {

      if(!m_manager.Initialize())
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



      return m_manager.Evaluate(
         trendScore,
         volatilityScore,
         liquidityScore,
         sessionScore);

   }



   //--------------------------------------------------

   CAIManager* GetManager()
   {
      return &m_manager;
   }


};


#endif

//+------------------------------------------------------------------+