//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionExecutor.mqh                                   |
//| Layer   : Core / AI                                              |
//| Version : 4.0.1                                                  |
//| Purpose : AI Decision Execution Adapter                          |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DECISIONEXECUTOR_MQH
#define CORE_AI_DECISIONEXECUTOR_MQH


#include "models/AIDecision.mqh"

#include "../execution/ExecutionManager.mqh"
#include "../execution/models/ExecutionContext.mqh"
#include "../execution/models/ExecutionResult.mqh"

#include "../decision/models/DecisionResult.mqh"


//+------------------------------------------------------------------+
//| AI Decision Executor                                             |
//+------------------------------------------------------------------+

class CDecisionExecutor
{

private:

   CExecutionManager *m_executionManager;


private:


   //--------------------------------------------------
   // Build Decision Result
   //--------------------------------------------------

   bool BuildDecisionResult(
      const CAIDecision &decision,
      CDecisionResult &result)
   {

      result.Reset();


      switch(decision.Action)
      {

         case AI_ACTION_BUY:

            result.Decision =
               DECISION_BUY;

            break;


         case AI_ACTION_SELL:

            result.Decision =
               DECISION_SELL;

            break;


         case AI_ACTION_CLOSE:

            // Current Decision Model
            // does not support CLOSE.
            // Convert to WAIT until model updated.

            result.Decision =
               DECISION_WAIT;

            break;


         default:

            return false;

      }



      result.Confidence =
         decision.Confidence;


      result.Valid = true;


      return true;

   }



   //--------------------------------------------------
   // Build Execution Context
   //--------------------------------------------------

   bool BuildExecutionContext(
      const CAIDecision &decision,
      CExecutionContext &context)
   {

      context.Reset();


      if(!BuildDecisionResult(
            decision,
            context.Decision))
      {
         return false;
      }


      context.Symbol =
         decision.Symbol;


      context.Timeframe =
         decision.Timeframe;


      context.CurrentTime =
         decision.Timestamp;


      return true;

   }



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CDecisionExecutor()
   {
      m_executionManager = NULL;
   }



   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize(
      CExecutionManager *executionManager)
   {

      if(executionManager == NULL)
         return false;


      m_executionManager =
         executionManager;


      return true;

   }



   //--------------------------------------------------
   // Execute Decision
   //--------------------------------------------------

   bool Execute(
      const CAIDecision &decision,
      CExecutionResult &result)
   {

      result.Success = false;


      if(!CanExecute(decision))
      {
         result.Message =
            "Invalid AI Decision.";

         return false;
      }


      if(m_executionManager == NULL)
      {
         result.Message =
            "Execution Manager unavailable.";

         return false;
      }



      CExecutionContext context;


      if(!BuildExecutionContext(
            decision,
            context))
      {

         result.Message =
            "Execution context build failed.";

         return false;

      }



      result =
         m_executionManager.Execute(
            context);



      return result.Success;

   }



   //--------------------------------------------------
   // Validation
   //--------------------------------------------------

   bool CanExecute(
      const CAIDecision &decision) const
   {

      if(!decision.Valid)
         return false;


      if(decision.Confidence <= 0.0)
         return false;



      switch(decision.Action)
      {

         case AI_ACTION_BUY:
         case AI_ACTION_SELL:

            return true;


         case AI_ACTION_CLOSE:
         case AI_ACTION_HOLD:
         case AI_ACTION_NONE:
         default:

            return false;

      }

   }

};


#endif

//+------------------------------------------------------------------+