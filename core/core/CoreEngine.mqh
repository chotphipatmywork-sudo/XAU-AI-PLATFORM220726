//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : CoreEngine.mqh                                         |
//| Layer   : Core                                                   |
//| Version : 1.0.1                                                  |
//| Purpose : Main Platform Engine                                   |
//+------------------------------------------------------------------+

#ifndef CORE_CORE_COREENGINE_MQH
#define CORE_CORE_COREENGINE_MQH


#include "../application/AIApplication.mqh"
#include "../application/ApplicationState.mqh"

#include "../system/SystemManager.mqh"


class CCoreEngine
{

private:

   CAIApplication     m_application;

   CSystemManager     m_systemManager;

   CApplicationState  m_state;


public:


   CCoreEngine()
   {
      m_state.Reset();
   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {

      m_state.Starting = true;


      if(!m_application.Initialize())
      {
         m_state.Starting = false;
         return false;
      }


      if(!m_systemManager.Initialize())
      {
         m_state.Starting = false;
         return false;
      }


      m_state.Starting = false;

      m_state.Initialized = true;

      m_state.Running = true;


      return true;
   }



   //--------------------------------------------------
   // Main Tick Process
   //--------------------------------------------------

   bool Process(
      string symbol,
      ENUM_TIMEFRAMES timeframe)
   {

      if(!m_state.Running)
         return false;


      m_systemManager.Update();


      return m_application.Process(
         symbol,
         timeframe);
   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

      m_systemManager.Shutdown();


      m_state.Running = false;

      m_state.Initialized = false;

   }



   //--------------------------------------------------
   // Status
   //--------------------------------------------------

   bool IsRunning()
   {
      return m_state.Running;
   }


};


#endif
//+------------------------------------------------------------------+