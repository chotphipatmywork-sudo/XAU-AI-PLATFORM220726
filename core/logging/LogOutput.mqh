//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LogOutput.mqh                                          |
//| Layer   : Core / Logging                                         |
//| Version : 1.0.0                                                  |
//| Purpose : Logging Output Interface                               |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_LOGOUTPUT_MQH
#define CORE_LOGGING_LOGOUTPUT_MQH


#include "LogEntry.mqh"


//--------------------------------------------------
// Logging Output Interface
//--------------------------------------------------

class ILogOutput
{

public:

   //--------------------------------------------------
   // Write Log Entry
   //--------------------------------------------------

   virtual void Write(
      const CLogEntry &entry)
   {
   }


   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   virtual bool Initialize()
   {
      return true;
   }


   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   virtual void Shutdown()
   {
   }

};


#endif

//+------------------------------------------------------------------+