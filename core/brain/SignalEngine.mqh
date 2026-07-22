//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SignalEngine.mqh                                       |
//| Layer   : Brain                                                  |
//| Version : 3.1.0                                                  |
//| Purpose : Signal Engine                                          |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SIGNALENGINE_MQH
#define CORE_BRAIN_SIGNALENGINE_MQH

#include "BrainAnalyzer.mqh"

#include "../engine/models/BrainPipelineResult.mqh"

//--------------------------------------------------

class CSignalEngine
{
private:

   CBrainAnalyzer m_brain;

public:

   //--------------------------------------------------

   CBrainPipelineResult Generate(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {
      CBrainPipelineResult result;

      //--------------------------------------------------
      // Analyze
      //--------------------------------------------------

      result.Analysis =
         m_brain.Analyze(
            symbol,
            timeframe,
            shift);

      //--------------------------------------------------
      // Signal
      //--------------------------------------------------

      result.Signal.type = SIGNAL_NONE;
      result.Signal.confidence = 0.0;
      result.Signal.source = "SignalEngine";
      result.Signal.reason = "";
      result.Signal.timestamp = TimeCurrent();

      //--------------------------------------------------

      result.Valid =
         result.Analysis.Valid;

      return result;
   }
};

#endif
