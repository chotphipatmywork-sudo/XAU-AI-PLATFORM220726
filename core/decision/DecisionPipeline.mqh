//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionPipeline.mqh                                   |
//| Layer   : Core / Decision                                        |
//| Version : 2.1.0                                                  |
//| Purpose : Decision Pipeline                                      |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_DECISIONPIPELINE_MQH
#define CORE_DECISION_DECISIONPIPELINE_MQH

#include "DecisionWorkspace.mqh"

#include "DecisionAnalyzer.mqh"

#include "DecisionAssembler.mqh"

//--------------------------------------------------

class CDecisionPipeline
{
private:

   CDecisionAnalyzer  m_analyzer;

   CDecisionAssembler m_assembler;

public:

   //--------------------------------------------------

   CDecisionResult Execute(
      const CBrainPipelineResult &brain)
   {
      CDecisionWorkspace workspace;

      workspace.Reset();

      //--------------------------------------------------
      // Brain Result
      //--------------------------------------------------

      workspace.Brain = brain;

      //--------------------------------------------------
      // Build Decision Context
      //--------------------------------------------------

      workspace.Context.Trend =
         brain.Analysis.Trend;

      workspace.Context.Volatility =
         brain.Analysis.Volatility;

      workspace.Context.Liquidity =
         brain.Analysis.Liquidity;

      workspace.Context.Session =
         brain.Analysis.Session;

      //--------------------------------------------------
      // Analyze
      //--------------------------------------------------

      workspace.Result =
         m_analyzer.Analyze(
            workspace.Context);

      //--------------------------------------------------
      // Assemble
      //--------------------------------------------------

      return
         m_assembler.Assemble(
            workspace.Result);
   }
};

#endif
