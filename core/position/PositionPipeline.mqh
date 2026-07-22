//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionPipeline.mqh                                  |
//| Layer   : Core / Execution                                       |
//| Version : 4.1.1                                                  |
//| Purpose : Execution Pipeline Controller with Lifecycle           |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTIONPIPELINE_MQH
#define CORE_EXECUTION_EXECUTIONPIPELINE_MQH


#include "models/ExecutionWorkspace.mqh"

#include "ExecutionAnalyzer.mqh"

#include "TradeRequestBuilder.mqh"
#include "OrderValidator.mqh"
#include "PositionChecker.mqh"

#include "assembler/ExecutionAssembler.mqh"


//--------------------------------------------------
// Execution Pipeline
//--------------------------------------------------

class CExecutionPipeline
{

private:

   CExecutionAnalyzer   m_analyzer;

   CTradeRequestBuilder m_builder;

   COrderValidator      m_validator;

   CPositionChecker     m_positionChecker;

   CExecutionAssembler  m_assembler;

   bool m_initialized;


public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CExecutionPipeline()
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
   // Validate Only
   //--------------------------------------------------

   bool Validate(
      const CExecutionContext &context)
   {

      if(!m_initialized)
         return false;


      CExecutionWorkspace workspace;

      workspace.Reset();


      workspace.Context = context;


      workspace.Result =
         m_analyzer.Analyze(
            workspace.Context);


      return m_validator.Validate(
         workspace.Context,
         workspace.Result);

   }



   //--------------------------------------------------
   // Execute
   //--------------------------------------------------

   CExecutionResult Execute(
      const CExecutionContext &context)
   {

      CExecutionResult result;


      if(!m_initialized)
         return result;



      CExecutionWorkspace workspace;


      workspace.Reset();


      workspace.Context = context;



      //--------------------------------------------------
      // Analyze
      //--------------------------------------------------

      workspace.Result =
         m_analyzer.Analyze(
            workspace.Context);



      //--------------------------------------------------
      // Validate
      //--------------------------------------------------

      if(!m_validator.Validate(
            workspace.Context,
            workspace.Result))
      {
         return workspace.Result;
      }



      //--------------------------------------------------
      // Position Check
      //--------------------------------------------------

      if(m_positionChecker.HasOpenPosition(
            workspace.Context.Symbol))
      {

         workspace.Result.Success = false;

         workspace.Result.Status =
            EXECUTION_REJECTED;

         workspace.Result.Message =
            "Position already exists.";

         return workspace.Result;
      }



      //--------------------------------------------------
      // Build Request
      //--------------------------------------------------

      m_builder.Build(
         workspace.Context,
         workspace.Result);



      //--------------------------------------------------
      // Assemble
      //--------------------------------------------------

      return
         m_assembler.Assemble(
            workspace.Result);

   }



   //--------------------------------------------------
   // Shutdown
   //--------------------------------------------------

   void Shutdown()
   {
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