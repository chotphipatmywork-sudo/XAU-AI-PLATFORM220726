//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIApplication.mqh                                      |
//| Layer   : Core / Application                                     |
//| Version : 1.0.1                                                  |
//| Purpose : Main AI System Controller                              |
//+------------------------------------------------------------------+

#ifndef CORE_APPLICATION_AIAPPLICATION_MQH
#define CORE_APPLICATION_AIAPPLICATION_MQH


#include "../brain/BrainAnalyzer.mqh"

#include "../ai/DecisionAdapter.mqh"

#include "../ai/DecisionExecutor.mqh"


//--------------------------------------------------
// AI Application Controller
//--------------------------------------------------

class CAIApplication
{

private:

   CBrainAnalyzer      m_brain;

   CDecisionAdapter    m_adapter;

   CDecisionExecutor   m_executor;


public:


   //--------------------------------------------------
   // Initialize
   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }



   //--------------------------------------------------
   // Main AI Processing Cycle
   //--------------------------------------------------

   bool Process(
      string symbol,
      ENUM_TIMEFRAMES timeframe)
   {


      //--------------------------------------------------
      // Brain Analysis
      //--------------------------------------------------

      CBrainAnalysisResult analysis =
         m_brain.Analyze(
            symbol,
            timeframe);



      if(!analysis.Valid)
      {
         return false;
      }



      //--------------------------------------------------
      // Risk Validation
      //--------------------------------------------------

      if(!analysis.Risk.AllowTrade)
      {
         return false;
      }



      //--------------------------------------------------
      // Generate AI Decision
      //--------------------------------------------------

      CAIDecision decision =
         m_adapter.Convert(
            analysis);



      if(!decision.IsValid())
      {
         return false;
      }



      //--------------------------------------------------
      // Execute Decision
      //--------------------------------------------------

      return m_executor.Execute(
         decision);

   }


};


#endif
//+------------------------------------------------------------------+