//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : NullOutput.mqh                                         |
//| Layer   : Core / Logging / Outputs                               |
//| Version : 1.0.0                                                  |
//| Purpose : Null Log Output                                        |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_OUTPUTS_NULLOUTPUT_MQH
#define CORE_LOGGING_OUTPUTS_NULLOUTPUT_MQH


#include "LogOutput.mqh"


//--------------------------------------------------
// Null Output
//--------------------------------------------------

class CNullOutput : public ILogOutput
{

public:


   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }



   //--------------------------------------------------
   // Write
   //--------------------------------------------------

   void Write(
      const CLogEntry &entry)
   {

      // Intentionally empty

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

   }


};


#endif

//+------------------------------------------------------------------+