//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LogEntry.mqh                                           |
//| Layer   : Core / Logging / Models                                |
//| Version : 1.0.0                                                  |
//| Purpose : Logging Data Model                                     |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_MODELS_LOGENTRY_MQH
#define CORE_LOGGING_MODELS_LOGENTRY_MQH


#include "LogLevel.mqh"


//--------------------------------------------------
// Log Entry Model
//--------------------------------------------------

class CLogEntry
{

public:

   //--------------------------------------------------
   // Data
   //--------------------------------------------------

   datetime Timestamp;

   ELogLevel Level;

   string Module;

   string Source;

   string Message;

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;



   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CLogEntry()
   {
      Reset();
   }



   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {

      Timestamp = 0;

      Level = LOG_LEVEL_INFO;

      Module = "";

      Source = "";

      Message = "";

      Symbol = "";

      Timeframe = PERIOD_CURRENT;

   }

};


#endif

//+------------------------------------------------------------------+