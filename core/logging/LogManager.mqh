//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LogManager.mqh                                         |
//| Layer   : Core / Logging                                         |
//| Version : 1.0.0                                                  |
//| Purpose : Logging Service Manager                                |
//+------------------------------------------------------------------+

#ifndef CORE_LOGGING_LOGMANAGER_MQH
#define CORE_LOGGING_LOGMANAGER_MQH


#include "LogFormatter.mqh"
#include "LogOutput.mqh"


//--------------------------------------------------
// Log Manager
//--------------------------------------------------

class CLogManager
{

private:

   CLogFormatter m_formatter;

   ILogOutput *m_output;

   bool m_initialized;



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CLogManager()
   {

      m_output = NULL;

      m_initialized = false;

   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize(
      ILogOutput *output)
   {

      if(output == NULL)
         return false;


      m_output = output;


      if(!m_output.Initialize())
         return false;


      m_initialized = true;


      return true;

   }



   //--------------------------------------------------
   // Write
   //--------------------------------------------------

   void Write(
      const CLogEntry &entry)
   {

      if(!m_initialized)
         return;


      if(m_output == NULL)
         return;


      CLogEntry formattedEntry = entry;


      formattedEntry.Message =
         m_formatter.Format(entry);


      m_output.Write(
         formattedEntry);

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

      if(m_output != NULL)
      {
         m_output.Shutdown();
      }


      m_output = NULL;


      m_initialized = false;

   }



   //--------------------------------------------------
   // Status
   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }


};


#endif

//+------------------------------------------------------------------+