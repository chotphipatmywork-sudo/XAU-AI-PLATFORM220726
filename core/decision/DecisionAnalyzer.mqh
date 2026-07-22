//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionAnalyzer.mqh                                   |
//| Layer   : Core / Decision                                        |
//| Version : 2.1.0                                                  |
//| Purpose : Decision Package Facade                                |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_DECISIONANALYZER_MQH
#define CORE_DECISION_DECISIONANALYZER_MQH

#include "models/DecisionContext.mqh"
#include "models/DecisionResult.mqh"

#include "engines/DecisionEngine.mqh"

//--------------------------------------------------
// Decision Analyzer
//--------------------------------------------------

class CDecisionAnalyzer
{
private:

   CDecisionEngine m_engine;

public:

   //--------------------------------------------------

   CDecisionResult Analyze(
      const CDecisionContext &context)
   {
      return m_engine.Evaluate(context);
   }
};

#endif
