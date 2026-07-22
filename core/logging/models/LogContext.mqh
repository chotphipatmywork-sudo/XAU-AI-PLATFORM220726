//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LogContext.mqh                                         |
//| Layer   : Core / Logging / Models                                |
//| Version : 1.0.0                                                  |
//| Purpose : Logging Context Model                                  |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_MODELS_LOGCONTEXT_MQH
#define CORE_LOGGING_MODELS_LOGCONTEXT_MQH


//--------------------------------------------------
// Log Context Model
//--------------------------------------------------

class CLogContext
{

public:

   //--------------------------------------------------
   // Context Data
   //--------------------------------------------------

   string Module;

   string Source;

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;

   ulong Ticket;

   datetime Timestamp;



   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CLogContext()
   {
      Reset();
   }



   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {

      Module = "";

      Source = "";

      Symbol = "";

      Timeframe = PERIOD_CURRENT;

      Ticket = 0;

      Timestamp = 0;

   }

};


#endif

//+------------------------------------------------------------------+