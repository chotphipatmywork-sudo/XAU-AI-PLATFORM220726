//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionManager.mqh                                   |
//| Layer   : Core / Execution                                       |
//| Version : 5.2.0                                                  |
//| Purpose : Execution Lifecycle Manager                            |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTIONMANAGER_MQH
#define CORE_EXECUTION_EXECUTIONMANAGER_MQH


#include "ExecutionPipeline.mqh"

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"


//--------------------------------------------------
// Execution Manager
//--------------------------------------------------

class CExecutionManager
{

private:

   CExecutionPipeline m_pipeline;

   bool m_initialized;



public:


   //--------------------------------------------------

   CExecutionManager()
   {
      m_initialized = false;
   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {

      m_initialized = true;

      return true;

   }



   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }



   //--------------------------------------------------
   // Execute
   //--------------------------------------------------

   CExecutionResult Execute(
      const CExecutionContext &context)
   {

      CExecutionResult result;


      if(!m_initialized)
      {

         result.Success = false;

         result.Message =
            "ExecutionManager not initialized.";

         return result;

      }



      return
         m_pipeline.Execute(
            context);

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

      m_initialized = false;

   }


};


#endif

//+------------------------------------------------------------------+