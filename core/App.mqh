//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : App.mqh                                                |
//| Layer   : Core                                                   |
//| Version : 4.1.0                                                  |
//| Purpose : Application Entry Controller                           |
//+------------------------------------------------------------------+

#ifndef CORE_APP_MQH
#define CORE_APP_MQH


#include "runtime/RuntimeManager.mqh"


//--------------------------------------------------
// Application
//--------------------------------------------------

class CApp
{

private:

   CRuntimeManager m_runtime;


public:


   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {
      return m_runtime.Initialize();
   }



   //--------------------------------------------------
   // Tick
   //--------------------------------------------------

   bool OnTick(
      const string symbol,
      ENUM_TIMEFRAMES timeframe)
   {

      m_runtime.SetContext(
         symbol,
         timeframe
      );


      m_runtime.OnTick();


      return true;
   }



   //--------------------------------------------------
   // Timer
   //--------------------------------------------------

   void OnTimer()
   {
      m_runtime.OnTimer();
   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {
      m_runtime.Shutdown();
   }

};


#endif

//+------------------------------------------------------------------+