//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionPipeline.mqh                                  |
//| Layer   : Core / Execution                                       |
//| Version : 4.0.2                                                  |
//| Purpose : Execution Pipeline Orchestrator                        |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTIONPIPELINE_MQH
#define CORE_EXECUTION_EXECUTIONPIPELINE_MQH


#include "engines/ExecutionEngine.mqh"

#include "TradeManager.mqh"

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"


//--------------------------------------------------
// Execution Pipeline
//--------------------------------------------------

class CExecutionPipeline
{

private:

   CExecutionEngine m_engine;

   CTradeManager m_tradeManager;



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CExecutionPipeline()
   {
   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }



   //--------------------------------------------------
   // Execute Pipeline
   //--------------------------------------------------

   CExecutionResult Execute(
      const CExecutionContext &context)
   {

      CExecutionResult result;


      //--------------------------------------------------
      // Step 1 : Build Execution Decision
      //--------------------------------------------------

      result =
         m_engine.Execute(
            context);



      if(!result.Success)
      {
         return result;
      }



      //--------------------------------------------------
      // Step 2 : Real Trade Execution
      //--------------------------------------------------

      if(!m_tradeManager.Execute(
            context,
            result))
      {
         return result;
      }



      return result;

   }



   //--------------------------------------------------
   // Position Check
   //--------------------------------------------------

   bool HasPosition(
      const string symbol) const
   {
      return m_tradeManager.HasPosition(
         symbol);
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