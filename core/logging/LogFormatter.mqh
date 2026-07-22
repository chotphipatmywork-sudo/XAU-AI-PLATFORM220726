//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LogFormatter.mqh                                       |
//| Layer   : Core / Logging                                         |
//| Version : 1.0.0                                                  |
//| Purpose : Log Message Formatter                                  |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_LOGFORMATTER_MQH
#define CORE_LOGGING_LOGFORMATTER_MQH


#include "LogEntry.mqh"


//--------------------------------------------------
// Log Formatter
//--------------------------------------------------

class CLogFormatter
{

public:


   //--------------------------------------------------
   // Format Log Entry
   //--------------------------------------------------

   string Format(
      const CLogEntry &entry)
   {

      string level = LevelToString(
         entry.Level);


      string output;


      output =
         "[" +
         level +
         "] ";


      if(entry.Module != "")
      {
         output +=
            "[" +
            entry.Module +
            "] ";
      }


      if(entry.Symbol != "")
      {
         output +=
            entry.Symbol +
            " ";
      }


      output +=
         entry.Message;


      return output;

   }



private:


   //--------------------------------------------------
   // Convert Level To String
   //--------------------------------------------------

   string LevelToString(
      const ELogLevel level)
   {

      switch(level)
      {

         case LOG_LEVEL_DEBUG:
            return "DEBUG";


         case LOG_LEVEL_INFO:
            return "INFO";


         case LOG_LEVEL_WARNING:
            return "WARNING";


         case LOG_LEVEL_ERROR:
            return "ERROR";

      }


      return "UNKNOWN";

   }


};


#endif

//+------------------------------------------------------------------+