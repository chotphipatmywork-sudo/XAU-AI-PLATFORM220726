//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Logger.mqh                                             |
//| Layer   : Infrastructure                                         |
//| Version : 2.0.0                                                  |
//| Purpose : System Logger Facade                                   |
//+------------------------------------------------------------------+

#ifndef CORE_INFRASTRUCTURE_LOGGER_MQH
#define CORE_INFRASTRUCTURE_LOGGER_MQH


#include "../logging/LogManager.mqh"
#include "../logging/LogLevel.mqh"
#include "../logging/LogEntry.mqh"
#include "../logging/outputs/JournalOutput.mqh"


//--------------------------------------------------
// Logger Facade
//--------------------------------------------------

class CLogger
{

private:

   static CLogManager m_manager;

   static CJournalOutput m_output;

   static bool m_initialized;



private:


   //--------------------------------------------------
   // Ensure Logger
   //--------------------------------------------------

   static void Ensure()
   {

      if(m_initialized)
         return;


      if(m_manager.Initialize(&m_output))
      {
         m_initialized = true;
      }

   }



   //--------------------------------------------------
   // Write
   //--------------------------------------------------

   static void Write(
      ELogLevel level,
      string text)
   {

      Ensure();


      if(!m_initialized)
         return;


      CLogEntry entry;


      entry.Level = level;

      entry.Message = text;

      entry.Timestamp = TimeCurrent();


      m_manager.Write(entry);

   }



public:


   //--------------------------------------------------
   // Info
   //--------------------------------------------------

   static void Info(
      string text)
   {

      Write(
         LOG_LEVEL_INFO,
         text);

   }



   //--------------------------------------------------
   // Warning
   //--------------------------------------------------

   static void Warning(
      string text)
   {

      Write(
         LOG_LEVEL_WARNING,
         text);

   }



   //--------------------------------------------------
   // Error
   //--------------------------------------------------

   static void Error(
      string text)
   {

      Write(
         LOG_LEVEL_ERROR,
         text);

   }



   //--------------------------------------------------
   // Debug
   //--------------------------------------------------

   static void Debug(
      string text)
   {

#ifdef _DEBUG

      Write(
         LOG_LEVEL_DEBUG,
         text);

#endif

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   static void Shutdown()
   {

      if(!m_initialized)
         return;


      m_manager.Shutdown();


      m_initialized = false;

   }

};


//--------------------------------------------------
// Static Members
//--------------------------------------------------

CLogManager CLogger::m_manager;

CJournalOutput CLogger::m_output;

bool CLogger::m_initialized = false;


#endif

//+------------------------------------------------------------------+