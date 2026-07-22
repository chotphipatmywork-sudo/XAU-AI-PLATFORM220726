//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Execution.mqh                                          |
//| Layer   : Core / Execution                                       |
//| Version : 3.0.0                                                  |
//| Purpose : Execution Facade                                       |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTION_MQH
#define CORE_EXECUTION_EXECUTION_MQH

#include "../ai/models/AIDecision.mqh"

#include "../trade/TradeLifecycle.mqh"

#include "ExecutionManager.mqh"

#include "builder/ExecutionContextBuilder.mqh"

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"

//--------------------------------------------------
// Execution Facade
//--------------------------------------------------

class CExecution
{

private:

   CExecutionManager        m_manager;

   CExecutionContextBuilder m_builder;

   CTradeLifecycle          m_tradeLifecycle;

public:

   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {

      if(!m_manager.Initialize())
         return false;

      return true;

   }

   //--------------------------------------------------
   // Execute AI Decision
   //--------------------------------------------------

   CExecutionResult Execute(
      const CAIDecision &decision)
   {

      CExecutionResult result;

      CExecutionContext context;

      //--------------------------------------------------
      // Build Context
      //--------------------------------------------------

      if(!m_builder.Build(
            decision,
            context))
      {
         result.Success = false;
         result.Message = "Unable to build execution context.";
         return result;
      }

      //--------------------------------------------------
      // Execute Pipeline
      //--------------------------------------------------

      result =
         m_manager.Execute(
            context);

      if(!result.Success)
         return result;

      //--------------------------------------------------
      // Start Trade Lifecycle
      //--------------------------------------------------

      if(!m_tradeLifecycle.StartFromExecution(
            context,
            result))
      {
         result.Success = false;
         result.Message =
            "TradeLifecycle initialization failed.";
      }

      return result;

   }

   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {

      m_manager.Shutdown();

   }

};

#endif

//+------------------------------------------------------------------+