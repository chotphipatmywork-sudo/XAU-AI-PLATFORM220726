//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : JournalOutput.mqh                                      |
//| Layer   : Core / Logging / Outputs                               |
//| Version : 1.0.0                                                  |
//| Purpose : Journal Log Output                                     |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_OUTPUTS_JOURNALOUTPUT_MQH
#define CORE_LOGGING_OUTPUTS_JOURNALOUTPUT_MQH


#include "../LogOutput.mqh"


//--------------------------------------------------
// Journal Output
//--------------------------------------------------

class CJournalOutput : public ILogOutput
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

      Print(
         entry.Message);

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