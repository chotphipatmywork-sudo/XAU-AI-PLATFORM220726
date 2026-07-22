//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionAnalyzer.mqh                                  |
//| Layer   : Core / Execution                                       |
//| Version : 3.0.0                                                  |
//| Purpose : Execution Package Facade                               |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTIONANALYZER_MQH
#define CORE_EXECUTION_EXECUTIONANALYZER_MQH

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"

#include "engines/ExecutionEngine.mqh"

//--------------------------------------------------
// Execution Analyzer
//--------------------------------------------------

class CExecutionAnalyzer
{
private:

   CExecutionEngine m_engine;

public:

   //--------------------------------------------------

   CExecutionResult Analyze(
      const CExecutionContext &context)
   {
      return
         m_engine.Execute(context);
   }
};

#endif